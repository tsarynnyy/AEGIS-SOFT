import { Text, View, StyleSheet, SafeAreaView, StatusBar, Platform } from "react-native";

export default function Index() {
  return (
    <SafeAreaView style={styles.safeArea}>
      <StatusBar barStyle="light-content" backgroundColor="#1a1a2e" />
      <View style={styles.container}>
        <View style={styles.header}>
          <Text style={styles.logo}>🛡️</Text>
          <Text style={styles.title}>Aegis AI</Text>
          <Text style={styles.subtitle}>Wellness Monitoring</Text>
        </View>
        
        <View style={styles.content}>
          <Text style={styles.description}>
            Proactive wellness monitoring for older adults and their care circles
          </Text>
          
          <View style={styles.statusCard}>
            <Text style={styles.statusLabel}>System Status</Text>
            <Text style={styles.statusValue}>✓ Connected</Text>
            <Text style={styles.statusDetail}>Platform: {Platform.OS}</Text>
          </View>
        </View>
        
        <View style={styles.footer}>
          <Text style={styles.footerText}>Aegis AI Platform v1.0</Text>
          <Text style={styles.footerSubtext}>Backend API Ready</Text>
        </View>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: "#1a1a2e",
  },
  container: {
    flex: 1,
    backgroundColor: "#1a1a2e",
    alignItems: "center",
    justifyContent: "space-between",
    paddingVertical: 40,
  },
  header: {
    alignItems: "center",
    marginTop: 60,
  },
  logo: {
    fontSize: 80,
    marginBottom: 20,
  },
  title: {
    fontSize: 36,
    fontWeight: "bold",
    color: "#ffffff",
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 18,
    color: "#a8b2d1",
    letterSpacing: 2,
    textTransform: "uppercase",
  },
  content: {
    flex: 1,
    alignItems: "center",
    justifyContent: "center",
    paddingHorizontal: 40,
  },
  description: {
    fontSize: 16,
    color: "#8892b0",
    textAlign: "center",
    lineHeight: 24,
    marginBottom: 40,
  },
  statusCard: {
    backgroundColor: "#16213e",
    borderRadius: 16,
    padding: 24,
    width: "100%",
    maxWidth: 320,
    borderWidth: 1,
    borderColor: "#0f3460",
  },
  statusLabel: {
    fontSize: 14,
    color: "#64ffda",
    marginBottom: 8,
    fontWeight: "600",
  },
  statusValue: {
    fontSize: 24,
    color: "#ffffff",
    fontWeight: "bold",
    marginBottom: 12,
  },
  statusDetail: {
    fontSize: 14,
    color: "#8892b0",
  },
  footer: {
    alignItems: "center",
    paddingBottom: 20,
  },
  footerText: {
    fontSize: 14,
    color: "#8892b0",
    marginBottom: 4,
  },
  footerSubtext: {
    fontSize: 12,
    color: "#64ffda",
  },
});
