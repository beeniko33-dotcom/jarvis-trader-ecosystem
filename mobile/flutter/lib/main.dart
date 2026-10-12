import 'dart:convert';

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
  Map<String, dynamic>? _live;

  Future<void> _load(String kind) async {
    setState(() {
      _loading = true;
      _error = null;
      _content = null;
      _live = null;
    });

    if (kind == 'live') {
      final data = await fetchLiveBotStatus();
      setState(() {
        _loading = false;
        if (data == null) {
          _error =
              'Live status failed. Is status_server.py running at $statusApiBase?';
        } else {
          _title = 'Live bot status';
          _live = data;
          _content = const JsonEncoder.withIndent('  ').convert(data);
        }
      });
      return;
    }

    final text = kind == 'status' ? await fetchStatusDoc() : await fetchReadme();
    setState(() {
      _loading = false;
      if (text == null) {
        _error = 'Failed to load document';
      } else {
        _title = kind == 'status' ? 'Project Status doc' : 'README';
        _content = text;
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    final paper = _live?['paper'] as Map<String, dynamic>?;
    final auto = _live?['autopilot'] as Map<String, dynamic>?;

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
                  children: [
                    const Text(
                      'Paper trading only',
                      style: TextStyle(
                        color: Color(0xFFF5C542),
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      'Live metrics from $statusApiBase. Bot control stays on Telegram.',
                      style: const TextStyle(color: Color(0xFFC5D0E6), height: 1.4),
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
                    onPressed: () => _load('live'),
                    child: const Text('Live bot'),
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: FilledButton.tonal(
                    onPressed: () => _load('status'),
                    child: const Text('Docs'),
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: FilledButton.tonal(
                    onPressed: () => _load('readme'),
                    child: const Text('README'),
                  ),
                ),
              ],
            ),
            if (_live != null) ...[
              const SizedBox(height: 12),
              Card(
                color: const Color(0xFF12182B),
                child: Padding(
                  padding: const EdgeInsets.all(12),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Balance: \$${(paper?['balance'] as num?)?.toStringAsFixed(2) ?? '—'}',
                      ),
                      Text(
                        'Autopilot: ${auto?['enabled'] == true ? 'ON' : 'OFF'} '
                        '(${auto?['mode']}/${auto?['risk']})',
                      ),
                      Text(
                        'Open: ${paper?['open_trades'] ?? 0} · '
                        'Closed PnL: ${paper?['closed_pnl'] ?? 0}',
                      ),
                      Text(
                        'Monitoring: ${_live!['monitoring'] == true ? 'yes' : 'no'}',
                      ),
                    ],
                  ),
                ),
              ),
            ],
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
                    _content!.length > 4000
                        ? _content!.substring(0, 4000)
                        : _content!,
                    style: const TextStyle(
                      color: Color(0xFFA8B6D1),
                      fontSize: 12,
                      height: 1.4,
                    ),
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
