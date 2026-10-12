import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  Pressable,
  ScrollView,
  ActivityIndicator,
  Linking,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { fetchRepoReadme, fetchStatusDoc } from './api';

export default function HomeScreen() {
  const [loading, setLoading] = useState(false);
  const [content, setContent] = useState(null);
  const [title, setTitle] = useState('');
  const [err, setErr] = useState(null);

  const load = async (kind) => {
    setLoading(true);
    setErr(null);
    setContent(null);
    const r = kind === 'status' ? await fetchStatusDoc() : await fetchRepoReadme();
    setLoading(false);
    if (r.ok) {
      setTitle(kind === 'status' ? 'Project Status' : 'README');
      setContent(r.data);
    } else {
      setErr(r.error);
    }
  };

  return (
    <SafeAreaView style={styles.safe}>
      <View style={styles.header}>
        <Text style={styles.brand}>JARVIS</Text>
        <Text style={styles.subtitle}>Trader Mobile Companion</Text>
      </View>

      <View style={styles.card}>
        <Text style={styles.cardTitle}>Paper trading only</Text>
        <Text style={styles.cardBody}>
          This app is a companion UI. Signals and autopilot run on the Python bot
          via Telegram. Do not use real funds until you have validated performance yourself.
        </Text>
      </View>

      <View style={styles.row}>
        <Pressable style={styles.btn} onPress={() => load('readme')}>
          <Text style={styles.btnText}>Load README</Text>
        </Pressable>
        <Pressable style={[styles.btn, styles.btnAlt]} onPress={() => load('status')}>
          <Text style={styles.btnText}>Load Status</Text>
        </Pressable>
      </View>

      <Pressable
        style={styles.linkBtn}
        onPress={() =>
          Linking.openURL('https://github.com/beeniko33-dotcom/jarvis-trader-ecosystem')
        }
      >
        <Text style={styles.linkText}>Open GitHub repository</Text>
      </Pressable>

      {loading && <ActivityIndicator color="#7C9CFF" style={{ marginTop: 16 }} />}
      {err && <Text style={styles.error}>{err}</Text>}

      {content && (
        <ScrollView style={styles.scroll}>
          <Text style={styles.docTitle}>{title}</Text>
          <Text style={styles.doc}>{content.slice(0, 4000)}</Text>
        </ScrollView>
      )}

      <Text style={styles.footer}>
        Bot control remains on Telegram. Mobile is for status and docs.
      </Text>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: '#0B1020', padding: 16 },
  header: { marginBottom: 16 },
  brand: { color: '#E8EEFF', fontSize: 28, fontWeight: '800', letterSpacing: 2 },
  subtitle: { color: '#8B9BB8', fontSize: 14, marginTop: 4 },
  card: {
    backgroundColor: '#151C33',
    borderRadius: 12,
    padding: 14,
    marginBottom: 14,
    borderWidth: 1,
    borderColor: '#243056',
  },
  cardTitle: { color: '#F5C542', fontWeight: '700', marginBottom: 6 },
  cardBody: { color: '#C5D0E6', fontSize: 13, lineHeight: 19 },
  row: { flexDirection: 'row', gap: 10, marginBottom: 10 },
  btn: {
    flex: 1,
    backgroundColor: '#3D5AFE',
    paddingVertical: 12,
    borderRadius: 10,
    alignItems: 'center',
  },
  btnAlt: { backgroundColor: '#2A3A66' },
  btnText: { color: '#fff', fontWeight: '700' },
  linkBtn: { paddingVertical: 10, alignItems: 'center' },
  linkText: { color: '#7C9CFF', fontSize: 13 },
  error: { color: '#FF6B6B', marginTop: 12 },
  scroll: { marginTop: 12, flex: 1 },
  docTitle: { color: '#E8EEFF', fontWeight: '700', marginBottom: 8 },
  doc: { color: '#A8B6D1', fontSize: 12, lineHeight: 18 },
  footer: { color: '#5C6B8A', fontSize: 11, textAlign: 'center', marginTop: 10 },
});
