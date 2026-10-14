// Census driver for RapidJSON (header-only): parse, walk, build and write a document.
// Never linked or run.
#include <string>
#include <vector>

#include "rapidjson/document.h"
#include "rapidjson/prettywriter.h"
#include "rapidjson/stringbuffer.h"
#include "rapidjson/writer.h"

using namespace rapidjson;

bool parse_doc(const char* s, Document& d) {
  d.Parse(s);
  return !d.HasParseError();
}
bool parse_insitu(char* s, Document& d) {
  d.ParseInsitu(s);
  return !d.HasParseError();
}
std::string write_doc(const Value& v) {
  StringBuffer sb;
  Writer<StringBuffer> w(sb);
  v.Accept(w);
  return sb.GetString();
}
std::string pretty_doc(const Value& v) {
  StringBuffer sb;
  PrettyWriter<StringBuffer> w(sb);
  v.Accept(w);
  return sb.GetString();
}
double sum_array(const Value& v) {
  double s = 0;
  for (const auto& e : v.GetArray()) s += e.GetDouble();
  return s;
}
void build_array(Document& d, const std::vector<double>& xs) {
  d.SetArray();
  for (double x : xs) d.PushBack(x, d.GetAllocator());
}
bool has_member(const Value& v, const char* k) { return v.IsObject() && v.HasMember(k); }
