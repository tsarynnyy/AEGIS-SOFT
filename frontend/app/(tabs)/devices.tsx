import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  ActivityIndicator,
  RefreshControl,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { useAuth } from '../../contexts/AuthContext';
import { api } from '../../services/api';

export default function DevicesScreen() {
  const { accessToken } = useAuth();
  const [memberProfile, setMemberProfile] = useState<any>(null);
  const [devices, setDevices] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);

  useEffect(() => {
    loadDevices();
  }, []);

  const loadDevices = async () => {
    if (!accessToken) return;

    setIsLoading(true);

    // Get member profile first
    const profileResponse = await api.getMemberProfile(accessToken);
    if (profileResponse.data) {
      setMemberProfile(profileResponse.data);

      // Get devices
      const devicesResponse = await api.getDevices(accessToken, profileResponse.data.id);
      if (devicesResponse.data) {
        setDevices(devicesResponse.data);
      }
    }

    setIsLoading(false);
  };

  const handleRefresh = async () => {
    setIsRefreshing(true);
    await loadDevices();
    setIsRefreshing(false);
  };

  const getDeviceIcon = (deviceType: string) => {
    switch (deviceType?.toLowerCase()) {
      case 'healthkit':
        return 'watch';
      case 'googlefit':
        return 'fitness';
      case 'fitbit':
        return 'watch-outline';
      case 'withings':
        return 'scale-outline';
      case 'mock':
        return 'phone-portrait-outline';
      default:
        return 'hardware-chip-outline';
    }
  };

  if (isLoading) {
    return (
      <SafeAreaView style={styles.safeArea} edges={['top']}>
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#64ffda" />
          <Text style={styles.loadingText}>Loading devices...</Text>
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
        <View style={styles.header}>
          <Text style={styles.title}>Connected Devices</Text>
          <Text style={styles.subtitle}>
            Manage your health data sources
          </Text>
        </View>

        {devices.length === 0 ? (
          <View style={styles.emptyState}>
            <Ionicons name="watch-outline" size={64} color="#8892b0" />
            <Text style={styles.emptyText}>No devices connected yet</Text>
            <Text style={styles.emptySubtext}>
              Connect your wearable devices to start monitoring your wellness
            </Text>
          </View>
        ) : (
          devices.map((device) => (
            <View key={device.id} style={styles.deviceCard}>
              <View style={styles.deviceHeader}>
                <View style={styles.deviceIconContainer}>
                  <Ionicons
                    name={getDeviceIcon(device.device_type) as any}
                    size={32}
                    color="#64ffda"
                  />
                </View>
                <View style={styles.deviceInfo}>
                  <Text style={styles.deviceName}>
                    {device.device_name || device.device_type}
                  </Text>
                  <Text style={styles.deviceType}>
                    {device.device_type.toUpperCase()}
                  </Text>
                </View>
                <View
                  style={[
                    styles.statusBadge,
                    device.is_active
                      ? styles.statusActive
                      : styles.statusInactive,
                  ]}
                >
                  <Text style={styles.statusText}>
                    {device.is_active ? 'Active' : 'Inactive'}
                  </Text>
                </View>
              </View>

              {device.last_sync_at && (
                <View style={styles.syncInfo}>
                  <Ionicons name="sync" size={16} color="#8892b0" />
                  <Text style={styles.syncText}>
                    Last synced: {new Date(device.last_sync_at).toLocaleString()}
                  </Text>
                </View>
              )}
            </View>
          ))
        )}

        <View style={styles.infoCard}>
          <Ionicons name="information-circle" size={24} color="#64ffda" />
          <Text style={styles.infoText}>
            Your devices automatically sync health data to provide real-time wellness insights.
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
  emptyState: {
    alignItems: 'center',
    padding: 40,
    backgroundColor: '#16213e',
    borderRadius: 16,
    borderWidth: 1,
    borderColor: '#0f3460',
  },
  emptyText: {
    fontSize: 18,
    fontWeight: '600',
    color: '#ffffff',
    marginTop: 16,
    marginBottom: 8,
  },
  emptySubtext: {
    fontSize: 14,
    color: '#8892b0',
    textAlign: 'center',
  },
  deviceCard: {
    backgroundColor: '#16213e',
    borderRadius: 16,
    padding: 20,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: '#0f3460',
  },
  deviceHeader: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  deviceIconContainer: {
    width: 56,
    height: 56,
    borderRadius: 28,
    backgroundColor: '#0f3460',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 16,
  },
  deviceInfo: {
    flex: 1,
  },
  deviceName: {
    fontSize: 18,
    fontWeight: '600',
    color: '#ffffff',
    marginBottom: 4,
  },
  deviceType: {
    fontSize: 12,
    color: '#8892b0',
    letterSpacing: 1,
  },
  statusBadge: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 12,
  },
  statusActive: {
    backgroundColor: 'rgba(16, 185, 129, 0.1)',
  },
  statusInactive: {
    backgroundColor: 'rgba(239, 68, 68, 0.1)',
  },
  statusText: {
    fontSize: 12,
    fontWeight: '600',
    color: '#10b981',
  },
  syncInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 12,
    paddingTop: 12,
    borderTopWidth: 1,
    borderTopColor: '#0f3460',
  },
  syncText: {
    fontSize: 12,
    color: '#8892b0',
    marginLeft: 8,
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
});
