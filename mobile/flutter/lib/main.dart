import 'package:flutter/material.dart';
import 'api_service.dart';

void main() => runApp(const JarvisApp());

class JarvisApp extends StatelessWidget {
  const JarvisApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Jarvis Trader',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        brightness: Brightness.dark,
        colorSchemeSeed: const Color(0xFF3D5AFE),
        useMaterial3: true,
      ),
      home: const HomePage(),
    );
  }
}

class HomePage extends StatefulWidget {
  const HomePage({super.key});

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  String? _content;
  String _title = '';
  bool _loading = false;
  String? _error;

  Future<void> _load(String kind) async {
    setState(() {
      _loading = true;
      _error = null;
      _content = null;
    });
    final text = kind == 'status' ? await fetchStatus() : await fetchReadme();
    setState(() {
      _loading = false;
      if (text == null) {
        _error = 'Failed to load document';
      } else {
        _title = kind == 'status' ? 'Project Status' : 'README';
        _content = text;
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0B1020),
      appBar: AppBar(
        title: const Text('JARVIS Trader'),
        backgroundColor: const Color(0xFF151C33),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Card(
              color: const Color(0xFF151C33),
              child: Padding(
                padding: const EdgeInsets.all(14),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: const [
                    Text(
                      'Paper trading only',
                      style: TextStyle(
                        color: Color(0xFFF5C542),
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    SizedBox(height: 8),
                    Text(
                      'Companion UI for docs and status. Bot control stays on Telegram. '
                      'Do not use real funds until you validate performance yourself.',
                      style: TextStyle(color: Color(0xFFC5D0E6), height: 1.4),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(
                  child: FilledButton(
                    onPressed: () => _load('readme'),
                    child: const Text('Load README'),
                  ),
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: FilledButton.tonal(
                    onPressed: () => _load('status'),
                    child: const Text('Load Status'),
                  ),
                ),
              ],
            ),
            if (_loading)
              const Padding(
                padding: EdgeInsets.only(top: 16),
                child: Center(child: CircularProgressIndicator()),
              ),
            if (_error != null)
              Padding(
                padding: const EdgeInsets.only(top: 12),
                child: Text(_error!, style: const TextStyle(color: Colors.redAccent)),
              ),
            if (_content != null) ...[
              const SizedBox(height: 12),
              Text(_title, style: const TextStyle(fontWeight: FontWeight.bold)),
              const SizedBox(height: 8),
              Expanded(
                child: SingleChildScrollView(
                  child: Text(
                    _content!.length > 4000 ? _content!.substring(0, 4000) : _content!,
                    style: const TextStyle(color: Color(0xFFA8B6D1), fontSize: 12, height: 1.4),
                  ),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}
