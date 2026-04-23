import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

void main() {
  runApp(const AIContentApp());
}

class AIContentApp extends StatelessWidget {
  const AIContentApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        brightness: Brightness.dark,
        primaryColor: const Color(0xFF1A237E),
        scaffoldBackgroundColor: const Color(0xFF0D1117),
        textTheme: GoogleFonts.poppinsTextTheme(Theme.of(context).textTheme)
            .apply(bodyColor: Colors.white),
      ),
      home: const ChatScreen(),
    );
  }
}

class ChatScreen extends StatefulWidget {
  const ChatScreen({super.key});

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final TextEditingController _controller = TextEditingController();
  final List<Map<String, String>> _messages = []; // Chat History သိမ်းရန်
  bool _isLoading = false;
  String selectedCategory = "General_Assistant";
  final List<String> categories = [
    "General_Assistant",
    "Networking",
    "Ruijie_Specialist",
    "Tech_Expert",
    "Computer_Hardware"
  ];

  // API သို့ စာပို့သည့် Function
  Future<void> _sendMessage() async {
    if (_controller.text.trim().isEmpty) return;

    String userMsg = _controller.text;
    setState(() {
      _messages.add({"role": "user", "content": userMsg});
      _isLoading = true;
    });
    _controller.clear();

    try {
      // Chrome နဲ့ စမ်းရင် 127.0.0.1:8000 သုံးပါ
      // ဖုန်းနဲ့ စမ်းရင် PC ရဲ့ IP Address (သို့) LocalTunnel URL ကို သုံးပါ
      final response = await http.post(
        Uri.parse('https://ai-specialist-expert.onrender.com/generate'),
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({
          "topic": userMsg,
          "category": selectedCategory,
        }),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        setState(() {
          _messages.add({"role": "ai", "content": data['content']});
        });
      } else {
        setState(() {
          _messages.add({"role": "ai", "content": "Error: Server နဲ့ ချိတ်ဆက်လို့ မရပါဘူးဗျာ။"});
        });
      }
    } catch (e) {
      setState(() {
        _messages.add({"role": "ai", "content": "Error: $e"});
      });
    } finally {
      setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("AI Specialist Expert"),
        elevation: 0,
        backgroundColor: const Color(0xFF1A237E),
        actions: [
          IconButton(
              onPressed: () => setState(() => _messages.clear()),
              icon: const Icon(Icons.delete_sweep))
        ],
      ),
      body: Column(
        children: [
          // Category Selector
          Container(
            height: 60,
            padding: const EdgeInsets.symmetric(vertical: 10),
            child: ListView.builder(
              scrollDirection: Axis.horizontal,
              itemCount: categories.length,
              itemBuilder: (context, index) {
                bool isSelected = selectedCategory == categories[index];
                return Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 5),
                  child: ChoiceChip(
                    label: Text(categories[index].replaceAll('_', ' ')),
                    selected: isSelected,
                    onSelected: (val) {
                      setState(() => selectedCategory = categories[index]);
                    },
                    selectedColor: Colors.amber[700],
                    labelStyle: TextStyle(
                        color: isSelected ? Colors.black : Colors.white),
                  ),
                );
              },
            ),
          ),

          // Chat Area
          Expanded(
            child: _messages.isEmpty
                ? const Center(child: Text("Specialist တစ်ယောက်ကို ရွေးပြီး မေးခွန်းမေးပါ"))
                : ListView.builder(
                    padding: const EdgeInsets.all(10),
                    itemCount: _messages.length,
                    itemBuilder: (context, index) {
                      bool isUser = _messages[index]['role'] == 'user';
                      return Align(
                        alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
                        child: Container(
                          margin: const EdgeInsets.symmetric(vertical: 5),
                          padding: const EdgeInsets.all(12),
                          decoration: BoxDecoration(
                            color: isUser ? Colors.amber[700] : Colors.grey[800],
                            borderRadius: BorderRadius.circular(15).copyWith(
                              bottomRight: isUser ? Radius.zero : const Radius.circular(15),
                              bottomLeft: isUser ? const Radius.circular(15) : Radius.zero,
                            ),
                          ),
                          child: Text(
                            _messages[index]['content']!,
                            style: TextStyle(color: isUser ? Colors.black : Colors.white),
                          ),
                        ),
                      );
                    },
                  ),
          ),

          if (_isLoading) const LinearProgressIndicator(color: Colors.amber),

          // Input Field
          Padding(
            padding: const EdgeInsets.all(12.0),
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _controller,
                    decoration: InputDecoration(
                      hintText: "$selectedCategory ကို မေးမြန်းပါ...",
                      border: OutlineInputBorder(borderRadius: BorderRadius.circular(30)),
                      filled: true,
                      fillColor: Colors.grey[900],
                      contentPadding: const EdgeInsets.symmetric(horizontal: 20),
                    ),
                    onSubmitted: (_) => _sendMessage(),
                  ),
                ),
                const SizedBox(width: 10),
                CircleAvatar(
                  backgroundColor: Colors.amber[700],
                  child: IconButton(
                    onPressed: _sendMessage,
                    icon: const Icon(Icons.send, color: Colors.black),
                  ),
                )
              ],
            ),
          ),
        ],
      ),
    );
  }
}