import 'package:flutter/material.dart';
import 'api_service.dart';

void main() => runApp(const JarvisApp());

class JarvisApp extends StatelessWidget {
  const JarvisApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Jarvis Trader',
      home: Scaffold(
        appBar: AppBar(title: const Text('Jarvis Trader')),
        body: const Center(child: HomeContent()),
      ),
    );
  }
}

class HomeContent extends StatefulWidget {
  const HomeContent({super.key});
  @override
  State<HomeContent> createState() => _HomeContentState();
}

class _HomeContentState extends State<HomeContent> {
  String? _readme;
  bool _loading = false;

  Future<void> _loadReadme() async {
    setState(() { _loading = true; _readme = null; });
    final res = await fetchReadme();
    setState(() { _loading = false; _readme = res ?? 'Failed to load'; });
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        const Text('Jarvis Trader - Flutter Demo', style: TextStyle(fontSize: 18)),
        const SizedBox(height: 12),
        ElevatedButton(onPressed: _loadReadme, child: const Text('Load README')),
        if (_loading) const Padding(padding: EdgeInsets.all(8), child: CircularProgressIndicator()),
        if (_readme != null) Padding(padding: const EdgeInsets.all(12), child: SizedBox(height:200, child: SingleChildScrollView(child: Text(_readme!)))),
      ],
    );
  }
}
