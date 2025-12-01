import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  ActivityIndicator,
  TouchableOpacity,
  RefreshControl,
  Alert,
  TextInput,
  Modal,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { useAuth } from '../../contexts/AuthContext';
import { api } from '../../services/api';

export default function CareCircleScreen() {
  const { accessToken } = useAuth();
  const [memberProfile, setMemberProfile] = useState<any>(null);
  const [caregivers, setCaregivers] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [showInviteModal, setShowInviteModal] = useState(false);
  const [inviteForm, setInviteForm] = useState({
    email: '',
    first_name: '',
    last_name: '',
    relationship: 'family',
  });
  const [isInviting, setIsInviting] = useState(false);

  useEffect(() => {
    loadCaregivers();
  }, []);

  const loadCaregivers = async () => {
    if (!accessToken) return;

    setIsLoading(true);

    // Get member profile
    const profileResponse = await api.getMemberProfile(accessToken);
    if (profileResponse.data) {
      setMemberProfile(profileResponse.data);

      // Get caregivers
      const caregiversResponse = await api.getCaregivers(
        accessToken,
        profileResponse.data.id
      );
      if (caregiversResponse.data) {
        setCaregivers(caregiversResponse.data);
      }
    }

    setIsLoading(false);
  };

  const handleRefresh = async () => {
    setIsRefreshing(true);
    await loadCaregivers();
    setIsRefreshing(false);
  };

  const handleInviteCaregiver = async () => {
    if (!inviteForm.email || !inviteForm.first_name || !inviteForm.last_name) {
      Alert.alert('Error', 'Please fill in all required fields');
      return;
    }

    if (!accessToken || !memberProfile) return;

    setIsInviting(true);

    const response = await api.inviteCaregiver(
      accessToken,
      memberProfile.id,
      inviteForm
    );

    setIsInviting(false);

    if (response.error) {
      Alert.alert('Error', response.error);
    } else {
      Alert.alert(
        'Success',
        `Invitation sent to ${inviteForm.first_name} ${inviteForm.last_name}`
      );
      setShowInviteModal(false);
      setInviteForm({
        email: '',
        first_name: '',
        last_name: '',
        relationship: 'family',
      });
      await loadCaregivers();
    }
  };

  const handleRemoveCaregiver = (caregiver: any) => {
    Alert.alert(
      'Remove Caregiver',
      `Remove ${caregiver.caregiver.first_name} ${caregiver.caregiver.last_name} from your care circle?`,
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Remove',
          style: 'destructive',
          onPress: async () => {
            const response = await api.removeCaregiver(accessToken!, caregiver.id);
            if (response.error) {
              Alert.alert('Error', response.error);
            } else {
              Alert.alert('Success', 'Caregiver removed');
              await loadCaregivers();
            }
          },
        },
      ]
    );
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'accepted':
        return '#10b981';
      case 'pending':
        return '#f59e0b';
      default:
        return '#8892b0';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'accepted':
        return 'checkmark-circle';
      case 'pending':
        return 'time';
      default:
        return 'help-circle';
    }
  };

  if (isLoading) {
    return (
      <SafeAreaView style={styles.safeArea} edges={['top']}>
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#64ffda" />
          <Text style={styles.loadingText}>Loading care circle...</Text>
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
          <Text style={styles.title}>Care Circle</Text>
          <Text style={styles.subtitle}>Family and caregivers monitoring your wellness</Text>
        </View>

        {/* Invite Button */}
        <TouchableOpacity
          style={styles.inviteButton}
          onPress={() => setShowInviteModal(true)}
        >
          <Ionicons name="person-add" size={24} color="#1a1a2e" />
          <Text style={styles.inviteButtonText}>Invite Caregiver</Text>
        </TouchableOpacity>

        {/* Caregivers List */}
        {caregivers.length === 0 ? (
          <View style={styles.emptyState}>
            <Ionicons name="people-outline" size={64} color="#8892b0" />
            <Text style={styles.emptyText}>No caregivers yet</Text>
            <Text style={styles.emptySubtext}>
              Invite family members or caregivers to monitor your wellness
            </Text>
          </View>
        ) : (
          caregivers.map((caregiver) => (
            <View key={caregiver.id} style={styles.caregiverCard}>
              <View style={styles.caregiverHeader}>
                <View style={styles.avatarContainer}>
                  <Text style={styles.avatarText}>
                    {caregiver.caregiver.first_name?.charAt(0) || 'C'}
                  </Text>
                </View>
                <View style={styles.caregiverInfo}>
                  <Text style={styles.caregiverName}>
                    {caregiver.caregiver.first_name} {caregiver.caregiver.last_name}
                  </Text>
                  <Text style={styles.caregiverRelationship}>
                    {caregiver.caregiver.relationship || 'Caregiver'}
                  </Text>
                </View>
                <TouchableOpacity
                  style={styles.removeButton}
                  onPress={() => handleRemoveCaregiver(caregiver)}
                >
                  <Ionicons name="close-circle" size={24} color="#ef4444" />
                </TouchableOpacity>
              </View>

              <View style={styles.caregiverDetails}>
                <View style={styles.statusRow}>
                  <Ionicons
                    name={getStatusIcon(caregiver.invitation_status) as any}
                    size={16}
                    color={getStatusColor(caregiver.invitation_status)}
                  />
                  <Text
                    style={[
                      styles.statusText,
                      { color: getStatusColor(caregiver.invitation_status) },
                    ]}
                  >
                    {caregiver.invitation_status}
                  </Text>
                </View>

                {/* Permissions */}
                <View style={styles.permissionsContainer}>
                  {caregiver.can_view_alerts && (
                    <View style={styles.permissionBadge}>
                      <Ionicons name="notifications" size={12} color="#64ffda" />
                      <Text style={styles.permissionText}>Alerts</Text>
                    </View>
                  )}
                  {caregiver.can_view_metrics && (
                    <View style={styles.permissionBadge}>
                      <Ionicons name="stats-chart" size={12} color="#64ffda" />
                      <Text style={styles.permissionText}>Metrics</Text>
                    </View>
                  )}
                </View>
              </View>
            </View>
          ))
        )}

        {/* Info Card */}
        <View style={styles.infoCard}>
          <Ionicons name="information-circle" size={24} color="#64ffda" />
          <Text style={styles.infoText}>
            Caregivers can monitor your wellness status and receive alerts when concerns are
            detected. You can manage their access anytime.
          </Text>
        </View>
      </ScrollView>

      {/* Invite Modal */}
      <Modal
        visible={showInviteModal}
        animationType="slide"
        presentationStyle="pageSheet"
        onRequestClose={() => setShowInviteModal(false)}
      >
        <SafeAreaView style={styles.modalContainer}>
          <View style={styles.modalHeader}>
            <TouchableOpacity onPress={() => setShowInviteModal(false)}>
              <Text style={styles.modalCancel}>Cancel</Text>
            </TouchableOpacity>
            <Text style={styles.modalTitle}>Invite Caregiver</Text>
            <View style={{ width: 60 }} />
          </View>

          <ScrollView style={styles.modalContent}>
            <Text style={styles.inputLabel}>First Name *</Text>
            <TextInput
              style={styles.input}
              placeholder="Enter first name"
              placeholderTextColor="#8892b0"
              value={inviteForm.first_name}
              onChangeText={(text) =>
                setInviteForm({ ...inviteForm, first_name: text })
              }
            />

            <Text style={styles.inputLabel}>Last Name *</Text>
            <TextInput
              style={styles.input}
              placeholder="Enter last name"
              placeholderTextColor="#8892b0"
              value={inviteForm.last_name}
              onChangeText={(text) => setInviteForm({ ...inviteForm, last_name: text })}
            />

            <Text style={styles.inputLabel}>Email *</Text>
            <TextInput
              style={styles.input}
              placeholder="caregiver@example.com"
              placeholderTextColor="#8892b0"
              value={inviteForm.email}
              onChangeText={(text) => setInviteForm({ ...inviteForm, email: text })}
              keyboardType="email-address"
              autoCapitalize="none"
            />

            <Text style={styles.inputLabel}>Relationship</Text>
            <View style={styles.relationshipButtons}>
              {['family', 'friend', 'professional'].map((rel) => (
                <TouchableOpacity
                  key={rel}
                  style={[
                    styles.relationshipButton,
                    inviteForm.relationship === rel && styles.relationshipButtonActive,
                  ]}
                  onPress={() => setInviteForm({ ...inviteForm, relationship: rel })}
                >
                  <Text
                    style={[
                      styles.relationshipButtonText,
                      inviteForm.relationship === rel && styles.relationshipButtonTextActive,
                    ]}
                  >
                    {rel.charAt(0).toUpperCase() + rel.slice(1)}
                  </Text>
                </TouchableOpacity>
              ))}
            </View>

            <TouchableOpacity
              style={[styles.sendButton, isInviting && styles.sendButtonDisabled]}
              onPress={handleInviteCaregiver}
              disabled={isInviting}
            >
              {isInviting ? (
                <ActivityIndicator color="#1a1a2e" />
              ) : (
                <Text style={styles.sendButtonText}>Send Invitation</Text>
              )}
            </TouchableOpacity>
          </ScrollView>
        </SafeAreaView>
      </Modal>
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
  inviteButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#64ffda',
    borderRadius: 12,
    padding: 16,
    marginBottom: 24,
  },
  inviteButtonText: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#1a1a2e',
    marginLeft: 8,
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
  caregiverCard: {
    backgroundColor: '#16213e',
    borderRadius: 16,
    padding: 20,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: '#0f3460',
  },
  caregiverHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  avatarContainer: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: '#64ffda',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  avatarText: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#1a1a2e',
  },
  caregiverInfo: {
    flex: 1,
  },
  caregiverName: {
    fontSize: 18,
    fontWeight: '600',
    color: '#ffffff',
    marginBottom: 2,
  },
  caregiverRelationship: {
    fontSize: 14,
    color: '#8892b0',
    textTransform: 'capitalize',
  },
  removeButton: {
    padding: 4,
  },
  caregiverDetails: {
    paddingTop: 12,
    borderTopWidth: 1,
    borderTopColor: '#0f3460',
  },
  statusRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  statusText: {
    fontSize: 14,
    fontWeight: '600',
    marginLeft: 6,
    textTransform: 'capitalize',
  },
  permissionsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  permissionBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(100, 255, 218, 0.1)',
    paddingHorizontal: 10,
    paddingVertical: 6,
    borderRadius: 8,
  },
  permissionText: {
    fontSize: 12,
    color: '#64ffda',
    marginLeft: 4,
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
  modalContainer: {
    flex: 1,
    backgroundColor: '#1a1a2e',
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#0f3460',
  },
  modalCancel: {
    fontSize: 16,
    color: '#64ffda',
  },
  modalTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#ffffff',
  },
  modalContent: {
    flex: 1,
    padding: 20,
  },
  inputLabel: {
    fontSize: 16,
    fontWeight: '600',
    color: '#64ffda',
    marginBottom: 8,
    marginTop: 16,
  },
  input: {
    backgroundColor: '#16213e',
    borderRadius: 12,
    padding: 16,
    fontSize: 16,
    color: '#ffffff',
    borderWidth: 1,
    borderColor: '#0f3460',
  },
  relationshipButtons: {
    flexDirection: 'row',
    gap: 12,
  },
  relationshipButton: {
    flex: 1,
    paddingVertical: 12,
    paddingHorizontal: 16,
    borderRadius: 12,
    backgroundColor: '#16213e',
    borderWidth: 1,
    borderColor: '#0f3460',
    alignItems: 'center',
  },
  relationshipButtonActive: {
    backgroundColor: 'rgba(100, 255, 218, 0.1)',
    borderColor: '#64ffda',
  },
  relationshipButtonText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#8892b0',
  },
  relationshipButtonTextActive: {
    color: '#64ffda',
  },
  sendButton: {
    backgroundColor: '#64ffda',
    borderRadius: 12,
    padding: 18,
    alignItems: 'center',
    marginTop: 32,
  },
  sendButtonDisabled: {
    opacity: 0.6,
  },
  sendButtonText: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1a1a2e',
  },
});
