import 'package:http/http.dart' as http;

const _rawBase =
    'https://raw.githubusercontent.com/beeniko33-dotcom/jarvis-trader-ecosystem/main';

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

Future<String?> fetchStatus() => _fetch('STATUS.md');
