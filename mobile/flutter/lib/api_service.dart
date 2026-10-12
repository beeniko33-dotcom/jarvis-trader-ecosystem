import 'dart:convert';

import 'package:http/http.dart' as http;

const _rawBase =
    'https://raw.githubusercontent.com/beeniko33-dotcom/jarvis-trader-ecosystem/main';

/// Override at build/run time if needed:
/// flutter run --dart-define=STATUS_URL=http://10.0.2.2:8787
const statusApiBase = String.fromEnvironment(
  'STATUS_URL',
  defaultValue: 'http://127.0.0.1:8787',
);

Future<String?> _fetch(String path) async {
  try {
    final url = Uri.parse('$_rawBase/$path');
    final res = await http.get(url).timeout(const Duration(seconds: 12));
    if (res.statusCode == 200) return res.body;
    return null;
  } catch (_) {
    return null;
  }
}

Future<String?> fetchReadme() => _fetch('README.md');

Future<String?> fetchStatusDoc() => _fetch('STATUS.md');

Future<Map<String, dynamic>?> fetchLiveBotStatus() async {
  try {
    final url = Uri.parse('$statusApiBase/status');
    final res = await http.get(url).timeout(const Duration(seconds: 8));
    if (res.statusCode != 200) return null;
    final decoded = jsonDecode(res.body);
    if (decoded is Map<String, dynamic>) return decoded;
    return null;
  } catch (_) {
    return null;
  }
}
