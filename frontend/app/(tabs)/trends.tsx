import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  ActivityIndicator,
  TouchableOpacity,
  Dimensions,
  RefreshControl,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { LineChart } from 'react-native-gifted-charts';
import { Ionicons } from '@expo/vector-icons';
import { useAuth } from '../../contexts/AuthContext';
import { api } from '../../services/api';

const { width: screenWidth } = Dimensions.get('window');
const chartWidth = screenWidth - 60;

export default function TrendsScreen() {
  const { accessToken } = useAuth();
  const [memberProfile, setMemberProfile] = useState<any>(null);
  const [metrics, setMetrics] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [timeRange, setTimeRange] = useState(7); // 7 or 30 days

  useEffect(() => {
    loadData();
  }, [timeRange]);

  const loadData = async () => {
    if (!accessToken) {
      console.log('No access token available');
      Alert.alert('Authentication Error', 'Please log in again');
      return;
    }

    setIsLoading(true);

    try {
      // Get member profile
      const profileResponse = await api.getMemberProfile(accessToken);
      
      if (profileResponse.error) {
        console.error('Profile error:', profileResponse.error);
        Alert.alert('Error', 'Failed to load profile. Please try logging in again.');
        setIsLoading(false);
        return;
      }
      
      if (profileResponse.data) {
        setMemberProfile(profileResponse.data);
        console.log('Member ID:', profileResponse.data.id);

        // Get metrics
        const metricsResponse = await api.getMetrics(
          accessToken,
          profileResponse.data.id,
          timeRange
        );
        
        if (metricsResponse.error) {
          console.error('Metrics error:', metricsResponse.error);
          Alert.alert('Error', 'Failed to load health data');
        } else if (metricsResponse.data) {
          console.log('Loaded metrics:', metricsResponse.data.length);
          setMetrics(metricsResponse.data);
        }
      }
    } catch (error) {
      console.error('Load data error:', error);
      Alert.alert('Error', 'Failed to load data');
    }

    setIsLoading(false);
  };

  const handleRefresh = async () => {
    setIsRefreshing(true);
    await loadData();
    setIsRefreshing(false);
  };

  const processChartData = (type: string) => {
    const filtered = metrics
      .filter((m) => m.type === type && m.value_num != null)
      .sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime());

    console.log(`Processing ${type}: filtered ${filtered.length} items from ${metrics.length} total`);

    if (filtered.length === 0) return [];

    const chartData = filtered.map((m, index) => ({
      value: parseFloat(m.value_num),
      label: index % Math.max(1, Math.floor(filtered.length / 5)) === 0
        ? new Date(m.timestamp).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
        : '',
    }));

    console.log(`Chart data for ${type}:`, chartData.slice(0, 3));
    return chartData;
  };

  const getMetricStats = (type: string) => {
    const filtered = metrics.filter((m) => m.type === type && m.value_num);
    if (filtered.length === 0) return { avg: 0, min: 0, max: 0 };

    const values = filtered.map((m) => m.value_num);
    return {
      avg: (values.reduce((a, b) => a + b, 0) / values.length).toFixed(1),
      min: Math.min(...values).toFixed(1),
      max: Math.max(...values).toFixed(1),
    };
  };

  if (isLoading) {
    return (
      <SafeAreaView style={styles.safeArea} edges={['top']}>
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#64ffda" />
          <Text style={styles.loadingText}>Loading your health trends...</Text>
        </View>
      </SafeAreaView>
    );
  }

  const hrvData = processChartData('hrv');
  const sleepData = processChartData('sleep_efficiency');
  const stepsData = processChartData('steps');
  const hrvStats = getMetricStats('hrv');
  const sleepStats = getMetricStats('sleep_efficiency');
  const stepsStats = getMetricStats('steps');

  console.log('Trends Screen - Total metrics:', metrics.length);
  console.log('HRV data points:', hrvData.length);
  console.log('Sleep data points:', sleepData.length);
  console.log('Steps data points:', stepsData.length);

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
          <Text style={styles.title}>Health Trends</Text>
          <Text style={styles.subtitle}>Your wellness data over time</Text>
        </View>

        {/* Time Range Selector */}
        <View style={styles.timeRangeContainer}>
          <TouchableOpacity
            style={[styles.timeButton, timeRange === 7 && styles.timeButtonActive]}
            onPress={() => setTimeRange(7)}
          >
            <Text style={[styles.timeButtonText, timeRange === 7 && styles.timeButtonTextActive]}>
              7 Days
            </Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={[styles.timeButton, timeRange === 30 && styles.timeButtonActive]}
            onPress={() => setTimeRange(30)}
          >
            <Text style={[styles.timeButtonText, timeRange === 30 && styles.timeButtonTextActive]}>
              30 Days
            </Text>
          </TouchableOpacity>
        </View>

        {/* HRV Chart */}
        {hrvData.length > 0 ? (
          <View style={styles.chartCard}>
            <View style={styles.chartHeader}>
              <View>
                <Text style={styles.chartTitle}>Heart Rate Variability</Text>
                <Text style={styles.chartSubtitle}>Higher is better</Text>
              </View>
              <View style={styles.statsContainer}>
                <Text style={styles.statLabel}>Avg</Text>
                <Text style={styles.statValue}>{hrvStats.avg} ms</Text>
              </View>
            </View>
            <View style={styles.chartContainer}>
              <LineChart
                data={hrvData}
                width={chartWidth}
                height={200}
                color="#10b981"
                thickness={2}
                curved
                areaChart
                startFillColor="#10b981"
                startOpacity={0.2}
                endOpacity={0}
                hideDataPoints
                hideRules
                yAxisTextStyle={{ color: '#8892b0' }}
                xAxisLabelTextStyle={{ color: '#8892b0' }}
                noOfSections={3}
              />
            </View>
            <View style={styles.statsRow}>
              <View style={styles.statItem}>
                <Text style={styles.statLabel}>Min</Text>
                <Text style={styles.statValue}>{hrvStats.min}</Text>
              </View>
              <View style={styles.statItem}>
                <Text style={styles.statLabel}>Max</Text>
                <Text style={styles.statValue}>{hrvStats.max}</Text>
              </View>
            </View>
          </View>
        ) : (
          <View style={styles.emptyCard}>
            <Text style={styles.emptyText}>No HRV data available for this period</Text>
          </View>
        )}

        {/* Sleep Efficiency Chart */}
        {sleepData.length > 0 && (
          <View style={styles.chartCard}>
            <View style={styles.chartHeader}>
              <View>
                <Text style={styles.chartTitle}>Sleep Efficiency</Text>
                <Text style={styles.chartSubtitle}>% of time asleep in bed</Text>
              </View>
              <View style={styles.statsContainer}>
                <Text style={styles.statLabel}>Avg</Text>
                <Text style={styles.statValue}>{(parseFloat(sleepStats.avg) * 100).toFixed(0)}%</Text>
              </View>
            </View>
            <LineChart
              data={sleepData.map(d => ({ ...d, value: d.value * 100 }))}
              width={chartWidth}
              height={220}
              adjustToWidth
              color="#8b5cf6"
              thickness={2}
              curved
              areaChart
              startFillColor="#8b5cf6"
              startOpacity={0.2}
              endOpacity={0}
              hideDataPoints
              hideRules
              yAxisTextStyle={{ color: '#8892b0' }}
              xAxisLabelTextStyle={{ color: '#8892b0' }}
              noOfSections={3}
              yAxisSuffix="%"
            />
            <View style={styles.statsRow}>
              <View style={styles.statItem}>
                <Text style={styles.statLabel}>Min</Text>
                <Text style={styles.statValue}>{(parseFloat(sleepStats.min) * 100).toFixed(0)}%</Text>
              </View>
              <View style={styles.statItem}>
                <Text style={styles.statLabel}>Max</Text>
                <Text style={styles.statValue}>{(parseFloat(sleepStats.max) * 100).toFixed(0)}%</Text>
              </View>
            </View>
          </View>
        )}

        {/* Steps Chart */}
        {stepsData.length > 0 && (
          <View style={styles.chartCard}>
            <View style={styles.chartHeader}>
              <View>
                <Text style={styles.chartTitle}>Daily Steps</Text>
                <Text style={styles.chartSubtitle}>Physical activity level</Text>
              </View>
              <View style={styles.statsContainer}>
                <Text style={styles.statLabel}>Avg</Text>
                <Text style={styles.statValue}>{parseFloat(stepsStats.avg).toFixed(0)}</Text>
              </View>
            </View>
            <LineChart
              data={stepsData}
              width={chartWidth}
              height={220}
              adjustToWidth
              color="#f59e0b"
              thickness={2}
              curved
              areaChart
              startFillColor="#f59e0b"
              startOpacity={0.2}
              endOpacity={0}
              hideDataPoints
              hideRules
              yAxisTextStyle={{ color: '#8892b0' }}
              xAxisLabelTextStyle={{ color: '#8892b0' }}
              noOfSections={3}
            />
            <View style={styles.statsRow}>
              <View style={styles.statItem}>
                <Text style={styles.statLabel}>Min</Text>
                <Text style={styles.statValue}>{parseFloat(stepsStats.min).toFixed(0)}</Text>
              </View>
              <View style={styles.statItem}>
                <Text style={styles.statLabel}>Max</Text>
                <Text style={styles.statValue}>{parseFloat(stepsStats.max).toFixed(0)}</Text>
              </View>
            </View>
          </View>
        )}

        {/* Info */}
        <View style={styles.infoCard}>
          <Ionicons name="information-circle" size={24} color="#64ffda" />
          <Text style={styles.infoText}>
            These charts show your health trends over time. Consistent patterns help us detect
            changes in your wellness.
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
  title: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#ffffff',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: '#8892b0',
  },
  timeRangeContainer: {
    flexDirection: 'row',
    marginBottom: 24,
    gap: 12,
  },
  timeButton: {
    flex: 1,
    paddingVertical: 12,
    paddingHorizontal: 20,
    borderRadius: 12,
    backgroundColor: '#16213e',
    borderWidth: 2,
    borderColor: '#0f3460',
    alignItems: 'center',
  },
  timeButtonActive: {
    backgroundColor: 'rgba(100, 255, 218, 0.1)',
    borderColor: '#64ffda',
  },
  timeButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#8892b0',
  },
  timeButtonTextActive: {
    color: '#64ffda',
  },
  chartCard: {
    backgroundColor: '#16213e',
    borderRadius: 16,
    padding: 20,
    marginBottom: 20,
    borderWidth: 1,
    borderColor: '#0f3460',
  },
  chartHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 16,
  },
  chartTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#ffffff',
    marginBottom: 4,
  },
  chartSubtitle: {
    fontSize: 13,
    color: '#8892b0',
  },
  statsContainer: {
    alignItems: 'flex-end',
  },
  statLabel: {
    fontSize: 12,
    color: '#8892b0',
    marginBottom: 2,
  },
  statValue: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#64ffda',
  },
  statsRow: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginTop: 16,
    paddingTop: 16,
    borderTopWidth: 1,
    borderTopColor: '#0f3460',
  },
  statItem: {
    alignItems: 'center',
  },
  infoCard: {
    flexDirection: 'row',
    backgroundColor: '#16213e',
    borderRadius: 16,
    padding: 16,
    borderWidth: 1,
    borderColor: '#0f3460',
    marginTop: 8,
  },
  infoText: {
    flex: 1,
    fontSize: 14,
    color: '#8892b0',
    marginLeft: 12,
    lineHeight: 20,
  },
  chartContainer: {
    marginVertical: 10,
    overflow: 'hidden',
  },
  emptyCard: {
    backgroundColor: '#16213e',
    borderRadius: 16,
    padding: 32,
    marginBottom: 20,
    borderWidth: 1,
    borderColor: '#0f3460',
    alignItems: 'center',
  },
  emptyText: {
    fontSize: 14,
    color: '#8892b0',
    textAlign: 'center',
  },
});
