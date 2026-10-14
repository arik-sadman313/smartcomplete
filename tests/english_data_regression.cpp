#include "predictor/predictor.h"
#include "predictor/grammar_rules.h"
#include "predictor/text_utils.h"

#include <cstdlib>
#include <filesystem>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

namespace {
namespace fs = std::filesystem;
int failures = 0;
int checks = 0;
void expect(bool value, const std::string& label) {
    ++checks;
    if (!value) { ++failures; std::cerr << "FAIL: " << label << '\n'; }
}
struct Home {
    bool existed = std::getenv("HOME") != nullptr;
    std::string old = existed ? std::getenv("HOME") : "";
    fs::path path;
    Home() {
        auto pattern = (fs::temp_directory_path() / "smartcomplete-english-XXXXXX").string();
        std::vector<char> bytes(pattern.begin(), pattern.end());
        bytes.push_back('\0');
        auto* result = mkdtemp(bytes.data());
        if (!result) throw std::runtime_error("mkdtemp failed");
        path = result;
        setenv("HOME", result, 1);
    }
    ~Home() {
        if (existed) setenv("HOME", old.c_str(), 1); else unsetenv("HOME");
        fs::remove_all(path);
    }
};
linuxcomplete::PredictorConfig config(const Home& home) {
    linuxcomplete::PredictorConfig cfg;
    cfg.dict_dir = std::string(ENGLISH_DATA_DIR) + "/dict";
    cfg.user_dict_path = (home.path / "user/learned.txt").string();
    cfg.max_candidates = 3;
    cfg.ai_rerank_enabled = false;
    return cfg;
}
void contains(const std::vector<linuxcomplete::Candidate>& list, const std::string& word,
              const std::string& label) {
    bool found = false;
    for (const auto& c : list)
        found |= linuxcomplete::text_utils::to_lower_ascii(c.word) == word;
    expect(found, label + " -> " + word + " in top three");
    expect(list.size() <= 3, label + " candidate limit");
}
void prefix(const std::string& input, const std::string& word) {
    Home home;
    linuxcomplete::Predictor predictor(config(home));
    expect(predictor.init(), "real dataset initializes");
    contains(predictor.predict(input), word, input);
}
void next(const std::vector<std::string>& context, const std::string& word) {
    Home home;
    linuxcomplete::Predictor predictor(config(home));
    expect(predictor.init(), "real dataset initializes");
    for (const auto& token : context) predictor.on_word_accepted(token);
    std::string label;
    for (const auto& token : context) label += token + " ";
    contains(predictor.predict_next_word(), word, label);
}
} // namespace

int main() {
    for (const auto& item : std::vector<std::pair<std::string, std::string>>{
        {"resch", "reschedule"}, {"onbo", "onboarding"},
        {"offbo", "offboarding"}, {"authent", "authentication"},
        {"reprod", "reproducible"}, {"unsub", "unsubscribe"},
        {"screensh", "screenshot"}, {"workfl", "workflow"},
        {"troublesh", "troubleshooting"}, {"accessib", "accessibility"},
        {"availab", "availability"}, {"notif", "notification"}}) {
        prefix(item.first, item.second);
    }
    next({"reschedule"}, "for");
    next({"onboarding"}, "process");
    next({"troubleshooting"}, "steps");
    next({"reproducible"}, "example");
    next({"can", "we"}, "reschedule the meeting");
    next({"thanks", "for"}, "your feedback");
    next({"would", "appreciate"}, "your feedback");
    next({"to", "reproduce"}, "the issue");
    next({"the", "attached"}, "document");

    // Existing high-signal suggestions must remain available.
    next({"how", "are"}, "you doing");
    next({"looking", "forward"}, "to hearing");
    next({"please", "let"}, "me know");
    {
        Home home;
        linuxcomplete::Predictor predictor(config(home));
        expect(predictor.init(), "boundary dataset initializes");
        expect(predictor.predict("").empty(), "empty prefix does not generate suggestions");
        expect(predictor.predict("r").empty(), "minimum prefix length preserved");
        expect(predictor.predict("zzzzqxv").empty(), "unknown prefix stays empty");
        contains(predictor.predict("RESCH"), "reschedule", "uppercase prefix");
    }
    linuxcomplete::set_rules_data_dir(std::string(ENGLISH_DATA_DIR) + "/rules");
    for (const auto& rule : std::vector<std::pair<std::string, std::string>>{
        {"responsible", "for"}, {"available", "for"}, {"reschedule", "for"},
        {"rescheduled", "for"}, {"reproducible", "example"}, {"troubleshooting", "steps"}}) {
        expect(linuxcomplete::lookup_pair_score(rule.first, rule.second) > 0,
               "natural pair: " + rule.first + " " + rule.second);
    }
    for (const auto& rule : std::vector<std::vector<std::string>>{
        {"can", "we", "reschedule"}, {"could", "you", "clarify"},
        {"i", "have", "attached"}, {"we", "have", "attached"},
        {"please", "find", "attached"}, {"thank", "you", "for"},
        {"let", "me", "know"}, {"would", "appreciate", "it"}}) {
        expect(linuxcomplete::lookup_triple_score(rule[0], rule[1], rule[2]) > 0,
               "natural triple: " + rule[0] + " " + rule[1] + " " + rule[2]);
    }
    expect(linuxcomplete::lookup_triple_score("i", "have", "attach") <= 0,
           "do not reward incorrect perfect tense: i have attach");
    expect(linuxcomplete::lookup_triple_score("can", "we", "rescheduled") <= 0,
           "do not reward inflected verb after modal: can we rescheduled");
    expect(linuxcomplete::lookup_pair_score("interested", "in") > 0,
           "existing preposition rule preserved");
    std::cout << "English data: " << checks << " checks, " << failures << " failures\n";
    return failures ? 1 : 0;
}
