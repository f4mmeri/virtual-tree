#include <iostream>
#include <fstream>
#include <filesystem>
#include <vector>
#include <set>
#include <string>
#include <algorithm>
#include <utility>
using namespace std;

struct Event { string type; int a, b, c; vector<int> stack; };

struct Tree {
    int n, root, LOG = 1, timer = 0;
    vector<pair<int,int>> edges;
    vector<vector<int>> adj, up;
    vector<int> tin, tout, depth;

    Tree(int n_, int root_, const vector<pair<int,int>>& e)
        : n(n_), root(root_), edges(e), adj(n_), tin(n_), tout(n_), depth(n_, 0) {
        while ((1 << LOG) < n) LOG++;
        up.assign(LOG, vector<int>(n, root));
        for (auto& [u, v] : edges) { adj[u].push_back(v); adj[v].push_back(u); }
        dfs(root, root);
    }
    void dfs(int v, int p) {
        tin[v] = timer++;
        up[0][v] = p;
        for (int j = 1; j < LOG; j++) up[j][v] = up[j-1][up[j-1][v]];
        for (int u : adj[v]) if (u != p) { depth[u] = depth[v] + 1; dfs(u, v); }
        tout[v] = timer++;
    }
    bool isAnc(int u, int v) const { return tin[u] <= tin[v] && tout[v] <= tout[u]; }
    int lca(int u, int v) const {
        if (isAnc(u, v)) return u;
        if (isAnc(v, u)) return v;
        for (int j = LOG - 1; j >= 0; j--)
            if (!isAnc(up[j][u], v)) u = up[j][u];
        return up[0][u];
    }
};

struct VTResult {
    vector<int> nodes;
    vector<pair<int,int>> edges;
    vector<Event> events;
};

VTResult buildVirtualTree(const Tree& t, vector<int> keys) {
    VTResult r;
    set<int> nodes = {t.root};
    vector<int> st = {t.root};

    auto emit = [&](const char* type, int a, int b, int c, const vector<int>& s) {
        r.events.push_back({type, a, b, c, s});
    };
    auto addEdge = [&](int p, int c) {
        r.edges.push_back({p, c});
        nodes.insert(p); nodes.insert(c);
        emit("edge", p, c, -1, st);
    };
    auto popTop = [&]() {
        int x = st.back(); st.pop_back();
        emit("pop", x, -1, -1, st);
    };

    sort(keys.begin(), keys.end(), [&](int a, int b) { return t.tin[a] < t.tin[b]; });
    keys.erase(unique(keys.begin(), keys.end()), keys.end());
    emit("sort", -1, -1, -1, keys);
    emit("start", t.root, -1, -1, st);

    for (int v : keys) {
        if (v == t.root) continue;
        emit("visit", v, st.back(), -1, st);
        int l = t.lca(v, st.back());
        emit("lca", v, st.back(), l, st);
        if (l != st.back()) {
            while (st.size() >= 2 && t.depth[st[st.size() - 2]] >= t.depth[l]) {
                addEdge(st[st.size() - 2], st.back());
                popTop();
            }
            if (st.back() != l) {
                addEdge(l, st.back());
                int old = st.back();
                st.back() = l;
                nodes.insert(l);
                emit("replace", old, l, -1, st);
            }
        }
        st.push_back(v);
        nodes.insert(v);
        emit("push", v, -1, -1, st);
    }
    while (st.size() >= 2) { addEdge(st[st.size() - 2], st.back()); popTop(); }
    emit("finish", -1, -1, -1, st);

    r.nodes.assign(nodes.begin(), nodes.end());
    return r;
}

string arr(const vector<int>& v) {
    string s = "[";
    for (size_t i = 0; i < v.size(); i++) { if (i) s += ","; s += to_string(v[i]); }
    return s + "]";
}

void writeLog(const string& path, const Tree& t, const vector<int>& keys, const VTResult& r) {
    ofstream f(path);
    f << "{\n\"tree\":{\"n\":" << t.n << ",\"root\":" << t.root << ",\"edges\":[";
    for (size_t i = 0; i < t.edges.size(); i++)
        f << (i ? "," : "") << "[" << t.edges[i].first << "," << t.edges[i].second << "]";
    f << "]},\n\"keys\":" << arr(keys) << ",\n\"depth\":" << arr(t.depth)
      << ",\n\"nodes\":" << arr(r.nodes) << ",\n\"events\":[\n";
    for (size_t i = 0; i < r.events.size(); i++) {
        const Event& e = r.events[i];
        f << (i ? ",\n" : "") << "{\"t\":\"" << e.type << "\",\"a\":" << e.a << ",\"b\":" << e.b
          << ",\"c\":" << e.c << ",\"stack\":" << arr(e.stack) << "}";
    }
    f << "\n]}\n";
}

int main() {
    filesystem::create_directories("logs");
    vector<pair<int,int>> E = {{0,1},{0,2},{1,3},{1,4},{2,5},{2,6},{3,7},{3,8},
                               {4,9},{4,10},{5,11},{6,12},{6,13},{13,14}};
    Tree t(15, 0, E);

    auto run = [&](const string& name, vector<int> keys) {
        VTResult r = buildVirtualTree(t, keys);
        writeLog("logs/vt_log_" + name + ".json", t, keys, r);
        cout << name << ": k=" << keys.size() << " -> " << r.nodes.size() << " nodos\n";
    };

    run("main", {8, 9, 11, 12});          // caso general
    run("single", {9});                   // k = 1
    run("chain", {1, 3, 8});              // clave que es ancestro de otra clave
    vector<int> all; for (int i = 1; i < t.n; i++) all.push_back(i);
    run("worstcase", all);                // todos los nodos son clave
}