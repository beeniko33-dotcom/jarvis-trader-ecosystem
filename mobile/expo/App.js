import React from 'react';
import { View, Text, StyleSheet, Button } from 'react-native';

export default function App() {
  const onPress = () => alert('Hello from Jarvis Expo!');
  return (
    <View style={styles.container}>
      <Text style={styles.title}>Jarvis Trader</Text>
      <Text style={styles.subtitle}>Mobile demo (Expo)</Text>
      <Button title="Ping API" onPress={onPress} />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, alignItems: 'center', justifyContent: 'center' },
  title: { fontSize: 28, fontWeight: '700', marginBottom: 8 },
  subtitle: { fontSize: 14, color: '#666', marginBottom: 16 }
});
