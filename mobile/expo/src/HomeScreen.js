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
import {
  fetchRepoReadme,
  fetchStatusDoc,
  fetchLiveBotStatus,
  STATUS_API_BASE,
} from './api';

export default function HomeScreen() {
  const [loading, setLoading] = useState(false);
  const [content, setContent] = useState(null);
  const [title, setTitle] = useState('');
  const [err, setErr] = useState(null);
  const [live, setLive] = useState(null);

  const load = async (kind) => {
    setLoading(true);
    setErr(null);
    setContent(null);
    setLive(null);

    if (kind === 'live') {
      const r = await fetchLiveBotStatus();
      setLoading(false);
      if (r.ok) {
        setTitle('Live bot status');
        setLive(r.data);
        setContent(JSON.stringify(r.data, null, 2));
      } else {
        setErr(r.error);
      }
      return;
    }

    const r = kind === 'status' ? await fetchStatusDoc() : await fetchRepoReadme();
    setLoading(false);
    if (r.ok) {
      setTitle(kind === 'status' ? 'Project Status doc' : 'README');
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
          Live status reads from status_server.py ({STATUS_API_BASE}). Trading
          control stays on Telegram. Validate performance before any real funds.
        </Text>
      </View>

      <View style={styles.row}>
        <Pressable style={styles.btn} onPress={() => load('live')}>
          <Text style={styles.btnText}>Live bot</Text>
        </Pressable>
        <Pressable style={[styles.btn, styles.btnAlt]} onPress={() => load('status')}>
          <Text style={styles.btnText}>Docs</Text>
        </Pressable>
        <Pressable style={[styles.btn, styles.btnAlt]} onPress={() => load('readme')}>
          <Text style={styles.btnText}>README</Text>
        </Pressable>
      </View>

      {live && (
        <View style={styles.metrics}>
          <Text style={styles.metric}>Balance: ${Number(live.paper?.balance ?? 0).toFixed(2)}</Text>
          <Text style={styles.metric}>
            Autopilot: {live.autopilot?.enabled ? 'ON' : 'OFF'} ({live.autopilot?.mode}/{live.autopilot?.risk})
          </Text>
          <Text style={styles.metric}>
            Open trades: {live.paper?.open_trades ?? 0} · Closed PnL: {live.paper?.closed_pnl ?? 0}
          </Text>
          <Text style={styles.metric}>
            Monitoring: {live.monitoring ? 'yes' : 'no'} · Pairs: {(live.active_forex_pairs || []).join(', ')}
          </Text>
        </View>
      )}

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
          <Text style={styles.doc}>{String(content).slice(0, 4000)}</Text>
        </ScrollView>
      )}

      <Text style={styles.footer}>
        Start API: python jarvis-trader-ecosystem/status_server.py
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
  row: { flexDirection: 'row', gap: 8, marginBottom: 10 },
  btn: {
    flex: 1,
    backgroundColor: '#3D5AFE',
    paddingVertical: 12,
    borderRadius: 10,
    alignItems: 'center',
  },
  btnAlt: { backgroundColor: '#2A3A66' },
  btnText: { color: '#fff', fontWeight: '700', fontSize: 12 },
  metrics: {
    backgroundColor: '#12182B',
    borderRadius: 10,
    padding: 12,
    marginBottom: 8,
    borderWidth: 1,
    borderColor: '#243056',
  },
  metric: { color: '#C5D0E6', fontSize: 12, marginBottom: 4 },
  linkBtn: { paddingVertical: 10, alignItems: 'center' },
  linkText: { color: '#7C9CFF', fontSize: 13 },
  error: { color: '#FF6B6B', marginTop: 12, fontSize: 12 },
  scroll: { marginTop: 12, flex: 1 },
  docTitle: { color: '#E8EEFF', fontWeight: '700', marginBottom: 8 },
  doc: { color: '#A8B6D1', fontSize: 12, lineHeight: 18 },
  footer: { color: '#5C6B8A', fontSize: 11, textAlign: 'center', marginTop: 10 },
});
