import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

void main() {
  runApp(const AIContentApp());
}

class AIContentApp extends StatefulWidget {
  const AIContentApp({super.key});

  @override
  State<AIContentApp> createState() => _AIContentAppState();
}

class _AIContentAppState extends State<AIContentApp> {
  // Theme အပြောင်းအလဲအတွက် variable
  bool _isDarkMode = true;

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Tech AI',
      debugShowCheckedModeBanner: false,
      // Light Theme configuration
      theme: ThemeData(
        brightness: Brightness.light,
        scaffoldBackgroundColor: const Color(0xFFF8FAFC), // နူးညံ့သော အဖြူရောင်
        primaryColor: const Color(0xFF3B82F6),
        appBarTheme: const AppBarTheme(
          backgroundColor: Colors.white,
          foregroundColor: Color(0xFF1E293B),
          elevation: 0.5,
        ),
        textTheme: GoogleFonts.interTextTheme(Theme.of(context).textTheme).apply(bodyColor: const Color(0xFF1E293B)),
      ),
      // Dark Theme configuration
      darkTheme: ThemeData(
        brightness: Brightness.dark,
        scaffoldBackgroundColor: const Color(0xFF0F172A),
        appBarTheme: const AppBarTheme(
          backgroundColor: Color(0xFF1E293B),
          elevation: 0,
        ),
        textTheme: GoogleFonts.interTextTheme(Theme.of(context).textTheme).apply(bodyColor: Colors.white),
      ),
      themeMode: _isDarkMode ? ThemeMode.dark : ThemeMode.light,
      home: ChatScreen(
        isDarkMode: _isDarkMode,
        onThemeChanged: (val) => setState(() => _isDarkMode = val),
      ),
    );
  }
}

class ChatScreen extends StatefulWidget {
  final bool isDarkMode;
  final Function(bool) onThemeChanged;

  const ChatScreen({super.key, required this.isDarkMode, required this.onThemeChanged});

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final TextEditingController _controller = TextEditingController();
  final List<Map<String, String>> _messages = [];
  bool _isLoading = false;
  String selectedCategory = "General_Assistant";
  final List<String> categories = ["General_Assistant", "Content_Writer","Networking", "Ruijie_Specialist", "Tech_Expert", "Computer_Hardware"];

  Future<void> _sendMessage() async {
    if (_controller.text.trim().isEmpty) return;
    String userMsg = _controller.text;
    setState(() {
      _messages.add({"role": "user", "content": userMsg});
      _isLoading = true;
    });
    _controller.clear();

    try {
      final response = await http.post(
        Uri.parse('https://ai-specialist-expert.onrender.com/generate'),
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({"topic": userMsg, "category": selectedCategory}),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        setState(() {
          _messages.add({"role": "ai", "content": data['content']});
        });
      } else {
        _showSnackBar("Server Error: နောက်မှ ပြန်ကြိုးစားကြည့်ပါဗျာ။");
      }
    } catch (e) {
      _showSnackBar("Connection Error: အင်တာနက် လိုင်းစစ်ပေးပါဦး။");
    } finally {
      setState(() => _isLoading = false);
    }
  }

  void _showSnackBar(String msg) {
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(msg)));
  }

  @override
  Widget build(BuildContext context) {
    final isDark = widget.isDarkMode;

    return Scaffold(
      appBar: AppBar(
        title: Text("Tech AI", style: GoogleFonts.inter(fontWeight: FontWeight.w700, letterSpacing: 0.5)),
        centerTitle: true,
        actions: [
          IconButton(
            icon: Icon(isDark ? Icons.light_mode_rounded : Icons.dark_mode_rounded),
            onPressed: () => widget.onThemeChanged(!isDark),
          ),
          IconButton(
            icon: const Icon(Icons.delete_outline_rounded),
            onPressed: () => setState(() => _messages.clear()),
          ),
        ],
      ),
      body: Column(
        children: [
          // Category Selector
          Container(
            height: 55,
            padding: const EdgeInsets.symmetric(vertical: 8),
            child: ListView.builder(
              scrollDirection: Axis.horizontal,
              padding: const EdgeInsets.symmetric(horizontal: 12),
              itemCount: categories.length,
              itemBuilder: (context, index) {
                bool isSelected = selectedCategory == categories[index];
                return Padding(
                  padding: const EdgeInsets.only(right: 8),
                  child: ChoiceChip(
                    label: Text(categories[index].replaceAll('_', ' ')),
                    selected: isSelected,
                    onSelected: (val) => setState(() => selectedCategory = categories[index]),
                    selectedColor: const Color(0xFF3B82F6),
                    backgroundColor: isDark ? const Color(0xFF334155) : const Color(0xFFE2E8F0),
                    labelStyle: TextStyle(
                      color: isSelected ? Colors.white : (isDark ? Colors.white70 : Colors.black87),
                      fontSize: 12,
                    ),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
                  ),
                );
              },
            ),
          ),

          // Chat View
          Expanded(
            child: _messages.isEmpty
                ? Center(
                    child: Opacity(
                      opacity: 0.5,
                      child: Column(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Icon(Icons.chat_bubble_outline_rounded, size: 60, color: isDark ? Colors.white : Colors.black),
                          const SizedBox(height: 10),
                          const Text("Specialist တစ်ယောက်ကို ရွေးပြီး မေးမြန်းနိုင်ပါပြီ"),
                        ],
                      ),
                    ),
                  )
                : ListView.builder(
                    padding: const EdgeInsets.all(16),
                    itemCount: _messages.length,
                    itemBuilder: (context, index) {
                      bool isUser = _messages[index]['role'] == 'user';
                      return _buildChatBubble(_messages[index]['content']!, isUser, isDark);
                    },
                  ),
          ),

          if (_isLoading) const LinearProgressIndicator(backgroundColor: Colors.transparent, minHeight: 2),

          // Input Area
          _buildInputSection(isDark),
        ],
      ),
    );
  }

  Widget _buildChatBubble(String content, bool isUser, bool isDark) {
    return Align(
      alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
      child: Column(
        crossAxisAlignment: isUser ? CrossAxisAlignment.end : CrossAxisAlignment.start,
        children: [
          Container(
            constraints: BoxConstraints(maxWidth: MediaQuery.of(context).size.width * 0.82),
            padding: const EdgeInsets.all(14),
            margin: const EdgeInsets.symmetric(vertical: 4),
            decoration: BoxDecoration(
              color: isUser 
                ? const Color(0xFF3B82F6) 
                : (isDark ? const Color(0xFF1E293B) : const Color(0xFFFFFFFF)),
              borderRadius: BorderRadius.circular(18).copyWith(
                bottomRight: isUser ? const Radius.circular(0) : const Radius.circular(18),
                bottomLeft: isUser ? const Radius.circular(18) : const Radius.circular(0),
              ),
              boxShadow: isDark ? [] : [BoxShadow(color: Colors.black.withOpacity(0.05), blurRadius: 5, offset: const Offset(0, 2))],
            ),
            child: SelectableText(
              content,
              style: TextStyle(
                color: isUser ? Colors.white : (isDark ? Colors.white : Colors.black87),
                fontSize: 15,
                height: 1.6,
                letterSpacing: 0.3,
              ),
            ),
          ),
          if (!isUser)
            Padding(
              padding: const EdgeInsets.only(left: 4, top: 2),
              child: InkWell(
                onTap: () {
                  Clipboard.setData(ClipboardData(text: content));
                  _showSnackBar("Copied to clipboard!");
                },
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(Icons.copy_rounded, size: 14, color: isDark ? Colors.white54 : Colors.black45),
                    const SizedBox(width: 4),
                    Text("Copy", style: TextStyle(fontSize: 12, color: isDark ? Colors.white54 : Colors.black45)),
                  ],
                ),
              ),
            ),
          const SizedBox(height: 12),
        ],
      ),
    );
  }

  Widget _buildInputSection(bool isDark) {
    return Container(
      padding: const EdgeInsets.fromLTRB(16, 12, 16, 24),
      decoration: BoxDecoration(
        color: isDark ? const Color(0xFF1E293B) : Colors.white,
        boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.05), blurRadius: 10, offset: const Offset(0, -2))],
      ),
      child: Row(
        children: [
          Expanded(
            child: TextField(
              controller: _controller,
              style: TextStyle(color: isDark ? Colors.white : Colors.black87),
              decoration: InputDecoration(
                hintText: "မေးခွန်းမေးမြန်းပါ...",
                hintStyle: TextStyle(color: isDark ? Colors.white38 : Colors.black38),
                filled: true,
                fillColor: isDark ? const Color(0xFF0F172A) : const Color(0xFFF1F5F9),
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(15), borderSide: BorderSide.none),
                contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
              ),
              onSubmitted: (_) => _sendMessage(),
            ),
          ),
          const SizedBox(width: 12),
          CircleAvatar(
            backgroundColor: const Color(0xFF3B82F6),
            radius: 24,
            child: IconButton(
              icon: const Icon(Icons.send_rounded, color: Colors.white, size: 20),
              onPressed: _sendMessage,
            ),
          ),
        ],
      ),
    );
  }
}