#include "engine/engine.h"
#include <fcitx/inputcontext.h>
#include <fcitx/inputcontextmanager.h>
#include <cstdlib>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

namespace {
int failures = 0;
#define EXPECT(x) do { if (!(x)) { std::cerr << "FAIL line " << __LINE__ << ": " #x "\n"; ++failures; } } while (0)

// Exercise the real engine and Fcitx key events; only the client is a test double.
class Client : public fcitx::InputContext {
public:
    explicit Client(fcitx::InputContextManager& manager, const std::string& program = "test-editor") : InputContext(manager, program) { created(); }
    ~Client() override { destroy(); }
    const char* frontend() const override { return "test"; }
    std::string committed;
    std::string displayed_preedit;
private:
    void commitStringImpl(const std::string& text) override { committed += text; }
    void deleteSurroundingTextImpl(int, unsigned int) override {}
    void forwardKeyImpl(const fcitx::ForwardKeyEvent&) override {}
    void updatePreeditImpl() override { displayed_preedit = inputPanel().clientPreedit().toString(); }
};

struct IsolatedHome {
    std::string previous = std::getenv("HOME") ? std::getenv("HOME") : "";
    bool had_home = std::getenv("HOME") != nullptr;
    std::filesystem::path path;
    IsolatedHome() {
        auto pattern = (std::filesystem::temp_directory_path() / "smartcomplete-shortcuts-XXXXXX").string();
        std::vector<char> name(pattern.begin(), pattern.end());
        name.push_back('\0');
        auto* result = mkdtemp(name.data());
        if (!result) throw std::runtime_error("mkdtemp failed");
        path = result;
        setenv("HOME", result, 1);
        auto dict = path / ".local/share/linuxcomplete/dict";
        std::filesystem::create_directories(dict);
        std::ofstream(dict / "en_US.txt") << "hello\nhelp\nhelmet\nhelper\nhelpful\n";
        auto frequency = dict.parent_path() / "frequency";
        std::filesystem::create_directories(frequency);
        std::ofstream(frequency / "en_freq.txt") << "hello 1000\nhelp 1000\nhelmet 1000\nhelper 1000\nhelpful 1000\n";
        auto ngram = dict.parent_path() / "ngram";
        std::filesystem::create_directories(ngram);
        std::ofstream(ngram / "en_bigrams.txt") << "hello help 100\nhello helmet 90\nhello helper 80\nhello helpful 70\n";
        auto emoji = dict.parent_path() / "emoji";
        std::filesystem::create_directories(emoji);
        std::ofstream(emoji / "en_emoji.tsv") << ":smile\t😊\t500\n:sad\t😢\t490\n:sun\t☀️\t480\n:star\t⭐\t470\n";
        auto config = path / ".config/linuxcomplete";
        std::filesystem::create_directories(config);
        std::ofstream(config / "linuxcomplete.conf")
            << R"({"max_candidates":8,"min_prefix_length":2,"min_candidate_score":0,"complete_word_extension_min_score":0,"ai_rerank_enabled":false})";
        // Never use a real provider during an engine test.
        setenv("LINUXCOMPLETE_AI_ENABLED", "0", 1);
    }
    ~IsolatedHome() {
        if (had_home) setenv("HOME", previous.c_str(), 1); else unsetenv("HOME");
        std::filesystem::remove_all(path);
    }
};

bool send(linuxcomplete::LinuxCompleteEngine& engine, Client& client,
          const fcitx::Key& key, bool release = false) {
    fcitx::InputMethodEntry entry("linuxcomplete", "SmartComplete", "en", "linuxcomplete");
    fcitx::KeyEvent event(&client, key, release);
    engine.keyEvent(entry, event);
    EXPECT(event.accepted() == event.filtered());
    return event.accepted();
}

void shortcuts() {
    const std::vector<fcitx::KeyStates> modifiers = {
        fcitx::KeyState::Ctrl, fcitx::KeyState::Alt,
        fcitx::KeyState::Ctrl_Shift, fcitx::KeyState::Alt_Shift,
        fcitx::KeyState::Ctrl_Alt
    };
    const std::vector<fcitx::KeySym> symbols = {
        FcitxKey_a, FcitxKey_Tab, FcitxKey_Return, FcitxKey_space,
        FcitxKey_Escape, FcitxKey_Up, FcitxKey_Down, FcitxKey_Left, FcitxKey_Right, FcitxKey_period,
        FcitxKey_BackSpace
    };
    for (auto states : modifiers) for (auto symbol : symbols) {
        fcitx::InputContextManager manager;
        Client client(manager);
        linuxcomplete::LinuxCompleteEngine engine(nullptr);
        EXPECT(send(engine, client, fcitx::Key(FcitxKey_h)));
        EXPECT(send(engine, client, fcitx::Key(FcitxKey_e)));
        EXPECT(client.inputPanel().candidateList() != nullptr);
        EXPECT(!send(engine, client, fcitx::Key(symbol, states)));
        EXPECT(client.committed == "he");
        EXPECT(client.inputPanel().candidateList() == nullptr);
        EXPECT(client.inputPanel().clientPreedit().toString().empty());
        EXPECT(!send(engine, client, fcitx::Key(symbol, states), true));
        EXPECT(client.committed == "he");
        EXPECT(send(engine, client, fcitx::Key(FcitxKey_z)));
        EXPECT(client.inputPanel().clientPreedit().toString() == "z");
    }
}

void empty_and_next_word() {
    for (auto state : {fcitx::KeyState::Ctrl, fcitx::KeyState::Alt}) {
        fcitx::InputContextManager manager;
        Client client(manager);
        linuxcomplete::LinuxCompleteEngine engine(nullptr);
        EXPECT(!send(engine, client, fcitx::Key(FcitxKey_c, state)));
        EXPECT(client.committed.empty());
        EXPECT(client.inputPanel().clientPreedit().toString().empty());
        for (char ch : std::string("hello"))
            EXPECT(send(engine, client, fcitx::Key(static_cast<fcitx::KeySym>(ch))));
        EXPECT(send(engine, client, fcitx::Key(FcitxKey_space)));
        EXPECT(client.committed == "hello ");
        EXPECT(client.inputPanel().candidateList() != nullptr);
        EXPECT(!send(engine, client, fcitx::Key(FcitxKey_Tab, state)));
        EXPECT(client.committed == "hello ");
        EXPECT(client.inputPanel().candidateList() == nullptr);
    }
}

void modifier_keys_and_shift() {
    for (auto symbol : {FcitxKey_Control_L, FcitxKey_Control_R, FcitxKey_Alt_L, FcitxKey_Alt_R}) {
        fcitx::InputContextManager manager;
        Client client(manager);
        linuxcomplete::LinuxCompleteEngine engine(nullptr);
        EXPECT(!send(engine, client, fcitx::Key(symbol)));
        EXPECT(client.committed.empty());
        EXPECT(client.inputPanel().candidateList() == nullptr);
        EXPECT(send(engine, client, fcitx::Key(FcitxKey_h)));
        EXPECT(!send(engine, client, fcitx::Key(symbol)));
        EXPECT(client.committed == "h");
        EXPECT(client.inputPanel().clientPreedit().toString().empty());
    }
    fcitx::InputContextManager manager;
    Client client(manager);
    linuxcomplete::LinuxCompleteEngine engine(nullptr);
    EXPECT(engine.listInputMethods().size() == 1);
    EXPECT(engine.listInputMethods().at(0).icon() == "linuxcomplete");
    EXPECT(send(engine, client, fcitx::Key(FcitxKey_H, fcitx::KeyState::Shift)));
    EXPECT(!send(engine, client, fcitx::Key(FcitxKey_Shift_L)));
    EXPECT(!send(engine, client, fcitx::Key(FcitxKey_Shift_R)));
    EXPECT(!send(engine, client, fcitx::Key(FcitxKey_Shift_L), true));
    EXPECT(send(engine, client, fcitx::Key(FcitxKey_E, fcitx::KeyState::Shift)));
    EXPECT(client.committed.empty());
    EXPECT(client.inputPanel().clientPreedit().toString().rfind("HE", 0) == 0);
    EXPECT(client.inputPanel().candidateList() != nullptr);
    EXPECT(send(engine, client, fcitx::Key(FcitxKey_Tab)));
    EXPECT(!client.committed.empty());
}

void compact_list() {
    for (const auto& input : {std::string("he"), std::string("hello "), std::string(":s")}) {
        for (auto accept : {FcitxKey_Tab, FcitxKey_Return}) {
            fcitx::InputContextManager manager;
            Client client(manager);
            linuxcomplete::LinuxCompleteEngine engine(nullptr);
            for (char ch : input)
                EXPECT(send(engine, client, fcitx::Key(static_cast<fcitx::KeySym>(ch))));
            auto list = client.inputPanel().candidateList();
            EXPECT(list != nullptr);
            if (!list) continue;
            EXPECT(list->layoutHint() == fcitx::CandidateLayoutHint::Horizontal);
            EXPECT(list->size() == 3);
            if (list->size() < 3) continue;
            EXPECT(list->toBulk()->totalSize() == 3);
            EXPECT(!list->toPageable()->hasNext());
            EXPECT(list->cursorIndex() == 0);
            for (auto direction : {FcitxKey_Right, FcitxKey_Down}) {
                for (int i = 1; i <= 6; ++i) {
                    EXPECT(send(engine, client, fcitx::Key(direction)));
                    EXPECT(list->cursorIndex() == i % 3);
                }
            }
            EXPECT(send(engine, client, fcitx::Key(FcitxKey_Left)));
            EXPECT(list->cursorIndex() == 2);
            EXPECT(send(engine, client, fcitx::Key(FcitxKey_Up)));
            EXPECT(list->cursorIndex() == 1);
            EXPECT(send(engine, client, fcitx::Key(FcitxKey_Right)));
            EXPECT(list->cursorIndex() == 2);
            std::string expected = list->candidate(2).text().toString();
            if (input == ":s") expected = expected.substr(0, expected.find(' '));
            // Existing commit behavior preserves a lowercase typed prefix even
            // when sentence-start suggestions are capitalized for display.
            if (input == "he" && expected[0] >= 'A' && expected[0] <= 'Z') expected[0] += 32;
            const auto before = client.committed;
            EXPECT(send(engine, client, fcitx::Key(accept)));
            EXPECT(client.committed == before + expected);
            EXPECT(client.inputPanel().candidateList() == nullptr);
            EXPECT(client.inputPanel().preedit().toString().empty());
            EXPECT(client.inputPanel().clientPreedit().toString().empty());
        }
    }
    // Clicking uses the same visible candidates and commit path as the keyboard.
    fcitx::InputContextManager manager;
    Client client(manager);
    linuxcomplete::LinuxCompleteEngine engine(nullptr);
    EXPECT(send(engine, client, fcitx::Key(FcitxKey_h)));
    EXPECT(send(engine, client, fcitx::Key(FcitxKey_e)));
    auto list = client.inputPanel().candidateList();
    EXPECT(list != nullptr);
    if (list && list->size() > 1) {
        auto expected = list->candidate(1).text().toString();
        if (expected[0] >= 'A' && expected[0] <= 'Z') expected[0] += 32;
        list->candidate(1).select(&client);
        EXPECT(client.committed == expected);
        EXPECT(client.inputPanel().candidateList() == nullptr);
        EXPECT(client.inputPanel().clientPreedit().toString().empty());
    }
    EXPECT(send(engine, client, fcitx::Key(FcitxKey_z)));
    EXPECT(send(engine, client, fcitx::Key(FcitxKey_z)));
    EXPECT(client.inputPanel().candidateList() == nullptr);
    EXPECT(!send(engine, client, fcitx::Key(FcitxKey_Left)));
    EXPECT(!send(engine, client, fcitx::Key(FcitxKey_Right)));
}


void url_fields() {
    for (const auto& program : {"microsoft-edge", "chromium", "firefox"}) {
        fcitx::InputContextManager manager;
        Client client(manager, program);
        linuxcomplete::LinuxCompleteEngine engine(nullptr);
        client.setCapabilityFlags(fcitx::CapabilityFlag::Url);
        for (auto key : {FcitxKey_h, FcitxKey_e, FcitxKey_l, FcitxKey_colon,
                        FcitxKey_slash, FcitxKey_period, FcitxKey_space,
                        FcitxKey_Tab, FcitxKey_Return, FcitxKey_BackSpace,
                        FcitxKey_Left, FcitxKey_Right, FcitxKey_Up, FcitxKey_Down}) {
            EXPECT(!send(engine, client, fcitx::Key(key)));
            EXPECT(client.committed.empty());
            EXPECT(client.inputPanel().candidateList() == nullptr);
            EXPECT(client.inputPanel().clientPreedit().toString().empty());
        }
        // A normal text field in the same browser still gets suggestions.
        client.setCapabilityFlags(fcitx::CapabilityFlag::NoFlag);
        EXPECT(send(engine, client, fcitx::Key(FcitxKey_h)));
        EXPECT(send(engine, client, fcitx::Key(FcitxKey_e)));
        auto oldList = client.inputPanel().candidateList();
        EXPECT(oldList != nullptr);
        client.setCapabilityFlags(fcitx::CapabilityFlag::Url);
        if (oldList) oldList->candidate(0).select(&client);
        EXPECT(client.committed.empty());
        EXPECT(client.inputPanel().candidateList() == nullptr);
        EXPECT(client.inputPanel().clientPreedit().toString().empty());
        client.setCapabilityFlags(fcitx::CapabilityFlag::NoFlag);
        EXPECT(send(engine, client, fcitx::Key(FcitxKey_h)));
        EXPECT(send(engine, client, fcitx::Key(FcitxKey_e)));
        // Changing field purpose must not commit the previous field's buffer.
        client.setCapabilityFlags(fcitx::CapabilityFlag::Url);
        EXPECT(!send(engine, client, fcitx::Key(FcitxKey_Tab)));
        EXPECT(client.committed.empty());
        EXPECT(client.inputPanel().candidateList() == nullptr);
        client.setCapabilityFlags(fcitx::CapabilityFlag::NoFlag);
        EXPECT(send(engine, client, fcitx::Key(FcitxKey_h)));
        EXPECT(send(engine, client, fcitx::Key(FcitxKey_e)));
        EXPECT(client.inputPanel().candidateList() != nullptr);
        EXPECT(send(engine, client, fcitx::Key(FcitxKey_Tab)));
        EXPECT(!client.committed.empty());
    }
}


void committed_text_replaces_preedit() {
    for (auto mode : {0, 1, 2, 3, 4}) {
        fcitx::InputContextManager manager;
        Client client(manager);
        client.setCapabilityFlags(fcitx::CapabilityFlag::Preedit);
        linuxcomplete::LinuxCompleteEngine engine(nullptr);
        EXPECT(send(engine, client, fcitx::Key(FcitxKey_h)));
        EXPECT(send(engine, client, fcitx::Key(FcitxKey_e)));
        EXPECT(client.displayed_preedit.size() > 2);
        EXPECT(client.displayed_preedit.rfind("he", 0) == 0);
        if (mode == 0) EXPECT(send(engine, client, fcitx::Key(FcitxKey_Tab)));
        if (mode == 1) EXPECT(send(engine, client, fcitx::Key(FcitxKey_Return)));
        if (mode == 2) {
            auto list = client.inputPanel().candidateList();
            EXPECT(list != nullptr);
            if (list) list->candidate(0).select(&client);
        }
        if (mode == 3) {
            EXPECT(!send(engine, client, fcitx::Key(FcitxKey_1)));
            EXPECT(client.committed == "he");
        }
        if (mode == 4) {
            EXPECT(send(engine, client, fcitx::Key(FcitxKey_period)));
            EXPECT(!client.committed.empty() && client.committed.back() == '.');
        }
        EXPECT(!client.committed.empty());
        EXPECT(client.displayed_preedit.empty());
        EXPECT(client.inputPanel().candidateList() == nullptr);
        const auto committed = client.committed;
        EXPECT(send(engine, client, fcitx::Key(FcitxKey_z)));
        EXPECT(client.displayed_preedit == "z");
        EXPECT(client.committed == committed);
    }
}

void contraction_preedit() {
    fcitx::InputContextManager manager;
    Client client(manager);
    client.setCapabilityFlags(fcitx::CapabilityFlag::Preedit);
    linuxcomplete::LinuxCompleteEngine engine(nullptr);
    EXPECT(send(engine, client, fcitx::Key(FcitxKey_i)));
    EXPECT(send(engine, client, fcitx::Key(FcitxKey_space)));
    for (char ch : std::string("dont"))
        EXPECT(send(engine, client, fcitx::Key(static_cast<fcitx::KeySym>(ch))));
    EXPECT(client.committed == "i ");
    // A correction inserts an apostrophe inside the word; it is not a suffix.
    EXPECT(client.displayed_preedit == "dont");
    auto list = client.inputPanel().candidateList();
    EXPECT(list != nullptr);
    if (list) EXPECT(list->candidate(0).text().toString() == "don't");
    EXPECT(send(engine, client, fcitx::Key(FcitxKey_Tab)));
    EXPECT(client.committed == "i don't");
    EXPECT(client.displayed_preedit.empty());
    EXPECT(client.inputPanel().candidateList() == nullptr);
    EXPECT(send(engine, client, fcitx::Key(FcitxKey_t)));
    EXPECT(client.displayed_preedit == "t");
    EXPECT(client.committed == "i don't");
}

} // namespace

int main() {
    IsolatedHome home;
    contraction_preedit();
    committed_text_replaces_preedit();
    url_fields();
    compact_list();
    shortcuts();
    empty_and_next_word();
    modifier_keys_and_shift();
    std::cout << "Engine shortcut failures: " << failures << '\n';
    return failures ? 1 : 0;
}
