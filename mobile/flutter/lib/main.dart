import 'package:flutter/material.dart';

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

class HomeContent extends StatelessWidget {
  const HomeContent({super.key});

  @override
  Widget build(BuildContext context) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        const Text('Jarvis Trader - Flutter Demo', style: TextStyle(fontSize: 18)),
        const SizedBox(height: 12),
        ElevatedButton(onPressed: () => _ping(context), child: const Text('Ping API'))
      ],
    );
  }

  void _ping(BuildContext context) {
    ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Hello from Jarvis Flutter')));
  }
}
