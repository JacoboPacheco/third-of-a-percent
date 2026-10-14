// Census driver for nlohmann/json (header-only): instantiates the common operations so the
// compiler generates (and reports on) their loops. Never linked or run.
#include <cstdint>
#include <string>
#include <vector>

#include "json.hpp"

using json = nlohmann::json;

json parse_text(const std::string& s) { return json::parse(s); }
bool accept_text(const std::string& s) { return json::accept(s); }
std::string dump_text(const json& j) { return j.dump(2); }
std::string dump_compact(const json& j) { return j.dump(); }
double sum_numbers(const json& j) {
  double s = 0;
  for (const auto& e : j)
    if (e.is_number()) s += e.get<double>();
  return s;
}
json from_vector(const std::vector<int>& v) { return json(v); }
std::vector<int> to_vector(const json& j) { return j.get<std::vector<int>>(); }
std::vector<std::uint8_t> to_cbor(const json& j) { return json::to_cbor(j); }
json from_cbor(const std::vector<std::uint8_t>& b) { return json::from_cbor(b); }
std::vector<std::uint8_t> to_msgpack(const json& j) { return json::to_msgpack(j); }
json diff(const json& a, const json& b) { return json::diff(a, b); }
json flatten(const json& j) { return j.flatten(); }
bool has_key(const json& j, const std::string& k) { return j.contains(k); }
const json& at_pointer(const json& j, const std::string& p) { return j.at(json::json_pointer(p)); }
