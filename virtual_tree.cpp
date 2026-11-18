#include <iostream>
#include <vector>
#include <string>
#include <sstream>
#include <fstream>
#include <algorithm>
using namespace std;

string toJson(const vector<int>& v) {
    ostringstream os;
    os << "[";
    for (size_t i = 0; i < v.size(); i++) {
        if (i) os << ",";
        os << v[i];
    }
    os << "]";
    return os.str();
}

struct Trace {
    bool enabled = false;
    vector<string> events;

    void add(const string& e) {
        if (enabled) events.push_back(e);
    }

    bool save(const string& path) const {
        ofstream f(path);
        if (!f) return false;
        f << "{\n  \"events\": [\n";
        for (size_t i = 0; i < events.size(); i++) {
            f << "    " << events[i];
            if (i + 1 < events.size()) f << ",";
            f << "\n";
        }
        f << "  ]\n}\n";
        return true;
    }
};

struct Tree {
    int n;
    int root;
    vector<vector<int>> kids;
    vector<int> par, tin, tout, depth, first, euler, lg;
    vector<vector<int>> sparse;
    int timer;
    Trace* trace;

    Tree(int nn, int r, const vector<int>& p, Trace* t = nullptr)
        : n(nn), root(r), kids(nn + 1), par(p), tin(nn + 1), tout(nn + 1),
          depth(nn + 1), first(nn + 1), timer(0), trace(t) {
        for (int v = 1; v <= n; v++)
            if (v != root) kids[par[v]].push_back(v);
    }

    bool on() const { return trace != nullptr && trace->enabled; }

    void prepare() {
        if (on()) {
            ostringstream os;
            os << "{\"op\":\"init_tree\",\"n\":" << n << ",\"root\":" << root << ",\"edges\":[";
            bool firstEdge = true;
            for (int v = 1; v <= n; v++) {
                if (v == root) continue;
                if (!firstEdge) os << ",";
                os << "[" << par[v] << "," << v << "]";
                firstEdge = false;
            }
            os << "]}";
            trace->add(os.str());
        }
        depth[root] = 0;
        dfs(root);
        buildSparse();
    }

    void dfs(int v) {
        tin[v] = timer++;
        first[v] = (int)euler.size();
        euler.push_back(v);
        if (on())
            trace->add("{\"op\":\"dfs_enter\",\"v\":" + to_string(v) + ",\"tin\":" + to_string(tin[v]) +
                       ",\"depth\":" + to_string(depth[v]) + "}");
        for (int c : kids[v]) {
            depth[c] = depth[v] + 1;
            dfs(c);
            euler.push_back(v);
        }
        tout[v] = timer++;
        if (on())
            trace->add("{\"op\":\"dfs_exit\",\"v\":" + to_string(v) + ",\"tout\":" + to_string(tout[v]) + "}");
    }

    void buildSparse() {
        int m = (int)euler.size();
        lg.assign(m + 1, 0);
        for (int i = 2; i <= m; i++) lg[i] = lg[i / 2] + 1;
        int levels = lg[m] + 1;
        sparse.assign(levels, vector<int>(m));
        sparse[0] = euler;
        for (int j = 1; j < levels; j++) {
            for (int i = 0; i + (1 << j) <= m; i++) {
                int a = sparse[j - 1][i];
                int b = sparse[j - 1][i + (1 << (j - 1))];
                sparse[j][i] = depth[a] <= depth[b] ? a : b;
            }
        }
    }

    bool isAncestor(int a, int b) const {
        return tin[a] <= tin[b] && tout[b] <= tout[a];
    }

    int lca(int a, int b) const {
        int l = first[a], r = first[b];
        if (l > r) swap(l, r);
        int j = lg[r - l + 1];
        int x = sparse[j][l];
        int y = sparse[j][r - (1 << j) + 1];
        return depth[x] <= depth[y] ? x : y;
    }
};

struct VirtualTree {
    const Tree& base;
    Trace* trace;
    vector<int> vpar;
    vector<vector<int>> vkids;
    vector<int> nodeList;
    vector<pair<int, int>> edgeList;
    int rootNode;

    VirtualTree(const Tree& t, Trace* tr = nullptr)
        : base(t), trace(tr), vpar(t.n + 1, 0), vkids(t.n + 1), rootNode(0) {}

    bool on() const { return trace != nullptr && trace->enabled; }

    void reset() {
        for (int v : nodeList) {
            vpar[v] = 0;
            vkids[v].clear();
        }
        nodeList.clear();
        edgeList.clear();
        rootNode = 0;
    }

    void build(const vector<int>& keys) {
        reset();
        if (on()) trace->add("{\"op\":\"query\",\"keys\":" + toJson(keys) + "}");

        auto byTin = [&](int a, int b) { return base.tin[a] < base.tin[b]; };
        vector<int> sorted = keys;
        sort(sorted.begin(), sorted.end(), byTin);
        sorted.erase(unique(sorted.begin(), sorted.end()), sorted.end());

        if (on()) {
            vector<int> tins;
            for (int v : sorted) tins.push_back(base.tin[v]);
            trace->add("{\"op\":\"sort\",\"before\":" + toJson(keys) + ",\"after\":" + toJson(sorted) +
                       ",\"tin\":" + toJson(tins) + "}");
        }

        if (sorted.empty()) return;

        vector<int> st;

        auto push = [&](int v) {
            st.push_back(v);
            nodeList.push_back(v);
            if (on())
                trace->add("{\"op\":\"push\",\"v\":" + to_string(v) + ",\"stack\":" + toJson(st) + "}");
        };

        auto pop = [&]() {
            int v = st.back();
            st.pop_back();
            if (on())
                trace->add("{\"op\":\"pop\",\"v\":" + to_string(v) + ",\"stack\":" + toJson(st) + "}");
        };

        auto link = [&](int p, int c) {
            edgeList.push_back({p, c});
            vpar[c] = p;
            vkids[p].push_back(c);
            if (on())
                trace->add("{\"op\":\"add_edge\",\"parent\":" + to_string(p) + ",\"child\":" + to_string(c) + "}");
        };

        for (int v : sorted) {
            if (st.empty()) {
                push(v);
                continue;
            }
            int top = st.back();
            int l = base.lca(v, top);
            if (on()) {
                bool isKey = binary_search(sorted.begin(), sorted.end(), l, byTin);
                trace->add("{\"op\":\"lca\",\"a\":" + to_string(v) + ",\"b\":" + to_string(top) +
                           ",\"result\":" + to_string(l) + ",\"is_key\":" + (isKey ? "true" : "false") + "}");
            }
            if (l == top) {
                push(v);
                continue;
            }
            while (st.size() >= 2 && base.depth[st[st.size() - 2]] >= base.depth[l]) {
                link(st[st.size() - 2], st.back());
                pop();
            }
            if (st.back() != l) {
                link(l, st.back());
                pop();
                push(l);
            }
            push(v);
        }
        while (st.size() >= 2) {
            link(st[st.size() - 2], st.back());
            pop();
        }
        rootNode = st.back();

        if (on()) {
            vector<int> ns = nodeList;
            sort(ns.begin(), ns.end(), byTin);
            string e = "{\"op\":\"result\",\"root\":" + to_string(rootNode) + ",\"nodes\":" + toJson(ns) + ",\"edges\":[";
            for (size_t i = 0; i < edgeList.size(); i++) {
                if (i) e += ",";
                e += "[" + to_string(edgeList[i].first) + "," + to_string(edgeList[i].second) + "]";
            }
            e += "]}";
            trace->add(e);
        }
    }

    int parent(int v) const { return vpar[v]; }
    const vector<int>& children(int v) const { return vkids[v]; }
    const vector<pair<int, int>>& edges() const { return edgeList; }
    const vector<int>& nodes() const { return nodeList; }
    int root() const { return rootNode; }
};

bool runScenario(const string& path, int n, const vector<int>& parent, const vector<int>& keys) {
    Trace trace;
    trace.enabled = true;
    Tree tree(n, 1, parent, &trace);
    tree.prepare();
    VirtualTree vt(tree, &trace);
    vt.build(keys);
    if (!trace.save(path)) {
        cerr << "No se pudo escribir " << path << "\n";
        return false;
    }
    cout << path << ": raiz " << vt.root() << ", " << vt.nodes().size() << " nodos, "
         << vt.edges().size() << " aristas\n";
    return true;
}

int main() {
    vector<int> parentMain = {0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 7};
    vector<int> keysMain = {11, 8, 6, 10};

    int nEdge = 15;
    vector<int> parentEdge(nEdge + 1, 0);
    for (int i = 2; i <= nEdge; i++) parentEdge[i] = i - 1;
    vector<int> keysEdge = {12, 3, 7};

    bool ok = true;
    ok = runScenario("logs/vt_log_main.json", 11, parentMain, keysMain) && ok;
    ok = runScenario("logs/vt_log_edge.json", nEdge, parentEdge, keysEdge) && ok;
    return ok ? 0 : 1;
}