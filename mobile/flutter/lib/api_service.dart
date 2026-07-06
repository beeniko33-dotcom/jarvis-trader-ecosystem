import 'package:http/http.dart' as http;

Future<String?> fetchReadme() async {
  try {
    final url = Uri.parse('https://raw.githubusercontent.com/beeniko33-dotcom/jarvis-trader-ecosystem/main/README.md');
    final res = await http.get(url).timeout(const Duration(seconds:10));
    if (res.statusCode == 200) return res.body;
    return null;
  } catch (e) {
    return null;
  }
}
