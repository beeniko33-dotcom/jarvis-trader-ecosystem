import React, {useState} from 'react';
import { View, Text, StyleSheet, Button, ScrollView, ActivityIndicator } from 'react-native';
import { fetchRepoReadme } from './api';

export default function HomeScreen() {
  const [loading, setLoading] = useState(false);
  const [readme, setReadme] = useState(null);
  const [err, setErr] = useState(null);

  const load = async () => {
    setLoading(true); setErr(null);
    const r = await fetchRepoReadme();
    setLoading(false);
    if (r.ok) setReadme(r.data);
    else setErr(r.error);
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Jarvis Trader</Text>
      <Text style={styles.subtitle}>Expo demo — README fetch</Text>
      <Button title="Load README" onPress={load} />
      {loading && <ActivityIndicator style={{marginTop:12}} />}
      {err && <Text style={{color:'red',marginTop:12}}>{err}</Text>}
      {readme && (
        <ScrollView style={{marginTop:12}}>
          <Text style={styles.readme}>{readme.slice(0,2000)}</Text>
        </ScrollView>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 16 },
  title: { fontSize: 24, fontWeight: '700', marginBottom: 6 },
  subtitle: { fontSize: 13, color: '#666', marginBottom: 12 },
  readme: { fontSize: 12, color: '#222' }
});
