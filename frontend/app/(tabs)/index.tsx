import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  ActivityIndicator,
  TouchableOpacity,
  RefreshControl,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useAuth } from '../../contexts/AuthContext';
import { api } from '../../services/api';

export default function DashboardScreen() {
  const { user, accessToken } = useAuth();
  const [memberProfile, setMemberProfile] = useState<any>(null);
  const [riskStatus, setRiskStatus] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    if (!accessToken) return;

    setIsLoading(true);

    // Get member profile
    const profileResponse = await api.getMemberProfile(accessToken);
    if (profileResponse.data) {
      setMemberProfile(profileResponse.data);

      // Get risk status
      const riskResponse = await api.getCurrentRisk(accessToken, profileResponse.data.id);
      if (riskResponse.data) {
        setRiskStatus(riskResponse.data);
      }
    }

    setIsLoading(false);
  };

  const handleRefresh = async () => {
    setIsRefreshing(true);
    await loadDashboardData();
    setIsRefreshing(false);
  };

  const getRiskColor = (tier: string) => {
    switch (tier?.toLowerCase()) {
      case 'green':
        return '#10b981';
      case 'yellow':
        return '#f59e0b';
      case 'red':
        return '#ef4444';
      default:
        return '#64ffda';
    }
  };

  const getRiskIcon = (tier: string) => {
    switch (tier?.toLowerCase()) {
      case 'green':
        return '✓';
      case 'yellow':
        return '⚡';
      case 'red':
        return '⚠️';
      default:
        return '🛡️';
    }
  };

  if (isLoading) {
    return (
      <SafeAreaView style={styles.safeArea} edges={['top']}>
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#64ffda" />
          <Text style={styles.loadingText}>Loading your wellness dashboard...</Text>
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.safeArea} edges={['top']}>
      <ScrollView
        style={styles.container}
        contentContainerStyle={styles.scrollContent}
        refreshControl={
          <RefreshControl
            refreshing={isRefreshing}
            onRefresh={handleRefresh}
            tintColor="#64ffda"
          />
        }
      >
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.greeting}>Welcome back,</Text>
          <Text style={styles.userName}>
            {memberProfile?.first_name || user?.first_name || 'Member'}
          </Text>
        </View>

        {/* Wellness Status Card */}
        <View style={[styles.statusCard, { borderColor: getRiskColor(riskStatus?.tier || 'green') }]}>
          <View style={styles.statusHeader}>
            <Text style={styles.statusIcon}>{getRiskIcon(riskStatus?.tier || 'green')}</Text>
            <View style={styles.statusInfo}>
              <Text style={styles.statusLabel}>Wellness Status</Text>
              <Text style={[styles.statusTier, { color: getRiskColor(riskStatus?.tier || 'green') }]}>
                {riskStatus?.tier ? riskStatus.tier.toUpperCase() : 'ALL GOOD'}
              </Text>
            </View>
          </View>

          {riskStatus?.explanation_text && (
            <View style={styles.explanationContainer}>
              <Text style={styles.explanationText}>{riskStatus.explanation_text}</Text>
            </View>
          )}

          {!riskStatus && (
            <View style={styles.explanationContainer}>
              <Text style={styles.explanationText}>
                All wellness indicators are within normal range. Keep up the great work!
              </Text>
            </View>
          )}
        </View>

        {/* Quick Stats */}
        <View style={styles.statsContainer}>
          <View style={styles.statCard}>
            <Text style={styles.statIcon}>❤️</Text>
            <Text style={styles.statLabel}>Heart</Text>
            <Text style={styles.statValue}>Normal</Text>
          </View>

          <View style={styles.statCard}>
            <Text style={styles.statIcon}>😴</Text>
            <Text style={styles.statLabel}>Sleep</Text>
            <Text style={styles.statValue}>Good</Text>
          </View>

          <View style={styles.statCard}>
            <Text style={styles.statIcon}>🚶</Text>
            <Text style={styles.statLabel}>Activity</Text>
            <Text style={styles.statValue}>Active</Text>
          </View>
        </View>

        {/* Suggested Actions */}
        {riskStatus?.suggested_actions && riskStatus.suggested_actions.length > 0 && (
          <View style={styles.actionsContainer}>
            <Text style={styles.actionsTitle}>Recommended Actions</Text>
            {riskStatus.suggested_actions.map((action: string, index: number) => (
              <View key={index} style={styles.actionItem}>
                <Text style={styles.actionBullet}>•</Text>
                <Text style={styles.actionText}>{action}</Text>
              </View>
            ))}
          </View>
        )}

        {/* Info Card */}
        <View style={styles.infoCard}>
          <Text style={styles.infoTitle}>About Your Wellness Score</Text>
          <Text style={styles.infoText}>
            Aegis AI monitors your health data from connected devices to detect changes in your
            wellness patterns. We analyze heart rate, sleep quality, activity levels, and more to
            provide proactive wellness insights.
          </Text>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: '#1a1a2e',
  },
  container: {
    flex: 1,
  },
  scrollContent: {
    padding: 20,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    fontSize: 16,
    color: '#8892b0',
    marginTop: 16,
  },
  header: {
    marginBottom: 24,
  },
  greeting: {
    fontSize: 18,
    color: '#8892b0',
  },
  userName: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#ffffff',
  },
  statusCard: {
    backgroundColor: '#16213e',
    borderRadius: 16,
    padding: 20,
    marginBottom: 20,
    borderWidth: 2,
  },
  statusHeader: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  statusIcon: {
    fontSize: 48,
    marginRight: 16,
  },
  statusInfo: {
    flex: 1,
  },
  statusLabel: {
    fontSize: 14,
    color: '#8892b0',
    marginBottom: 4,
  },
  statusTier: {
    fontSize: 24,
    fontWeight: 'bold',
  },
  explanationContainer: {
    marginTop: 16,
    paddingTop: 16,
    borderTopWidth: 1,
    borderTopColor: '#0f3460',
  },
  explanationText: {
    fontSize: 15,
    color: '#a8b2d1',
    lineHeight: 22,
  },
  statsContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 20,
  },
  statCard: {
    flex: 1,
    backgroundColor: '#16213e',
    borderRadius: 12,
    padding: 16,
    marginHorizontal: 4,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#0f3460',
  },
  statIcon: {
    fontSize: 32,
    marginBottom: 8,
  },
  statLabel: {
    fontSize: 12,
    color: '#8892b0',
    marginBottom: 4,
  },
  statValue: {
    fontSize: 14,
    fontWeight: '600',
    color: '#64ffda',
  },
  actionsContainer: {
    backgroundColor: '#16213e',
    borderRadius: 16,
    padding: 20,
    marginBottom: 20,
    borderWidth: 1,
    borderColor: '#f59e0b',
  },
  actionsTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#f59e0b',
    marginBottom: 12,
  },
  actionItem: {
    flexDirection: 'row',
    marginBottom: 8,
  },
  actionBullet: {
    fontSize: 16,
    color: '#f59e0b',
    marginRight: 8,
  },
  actionText: {
    flex: 1,
    fontSize: 15,
    color: '#a8b2d1',
    lineHeight: 22,
  },
  infoCard: {
    backgroundColor: '#16213e',
    borderRadius: 16,
    padding: 20,
    borderWidth: 1,
    borderColor: '#0f3460',
  },
  infoTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#64ffda',
    marginBottom: 8,
  },
  infoText: {
    fontSize: 14,
    color: '#8892b0',
    lineHeight: 20,
  },
});
