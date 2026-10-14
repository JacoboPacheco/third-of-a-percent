// Census driver for CLI11 (header-only): one app with options, a vector option, a subcommand
// and a validator. Never linked or run.
#include <string>
#include <vector>

#include "CLI/CLI.hpp"

int parse_args(int argc, char** argv) {
  CLI::App app{"census driver"};
  int n = 0;
  std::string file;
  std::vector<double> values;
  bool flag = false;
  app.add_option("-n,--number", n, "a number")->check(CLI::Range(0, 100));
  app.add_option("-f,--file", file, "a file")->check(CLI::ExistingFile);
  app.add_option("-v,--values", values, "some values");
  app.add_flag("--flag", flag, "a flag");
  auto* sub = app.add_subcommand("run", "a subcommand");
  std::string mode = "fast";
  sub->add_option("--mode", mode)->check(CLI::IsMember({"fast", "slow"}));
  try {
    app.parse(argc, argv);
  } catch (const CLI::ParseError& e) {
    return app.exit(e);
  }
  return n + int(values.size()) + int(flag);
}
std::string help_text() {
  CLI::App app{"census driver"};
  int n = 0;
  app.add_option("-n", n, "a number");
  return app.help();
}
