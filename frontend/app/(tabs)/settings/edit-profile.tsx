import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TextInput,
  TouchableOpacity,
  ActivityIndicator,
  Alert,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { useRouter } from 'expo-router';
import { useAuth } from '../../../contexts/AuthContext';
import { api } from '../../../services/api';

export default function EditProfileScreen() {
  const { accessToken } = useAuth();
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [memberProfile, setMemberProfile] = useState<any>(null);
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    emergency_contact_name: '',
    emergency_contact_phone: '',
    health_notes: '',
  });

  useEffect(() => {
    loadProfile();
  }, []);

  const loadProfile = async () => {
    if (!accessToken) return;

    const response = await api.getMemberProfile(accessToken);
    if (response.data) {
      setMemberProfile(response.data);
      setFormData({
        first_name: response.data.first_name || '',
        last_name: response.data.last_name || '',
        emergency_contact_name: response.data.emergency_contact_name || '',
        emergency_contact_phone: response.data.emergency_contact_phone || '',
        health_notes: response.data.health_notes || '',
      });
    }
    setIsLoading(false);
  };

  const handleSave = async () => {
    if (!accessToken || !memberProfile) return;

    setIsSaving(true);

    const response = await api.updateMemberProfile(accessToken, memberProfile.id, formData);

    setIsSaving(false);

    if (response.error) {
      Alert.alert('Error', response.error);
    } else {
      Alert.alert('Success', 'Profile updated successfully');
      router.back();
    }
  };

  if (isLoading) {
    return (
      <SafeAreaView style={styles.safeArea}>
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#64ffda" />
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.safeArea}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => router.back()} style={styles.backButton}>
          <Ionicons name="arrow-back" size={24} color="#64ffda" />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Edit Profile</Text>
        <View style={{ width: 24 }} />
      </View>

      <ScrollView style={styles.container} contentContainerStyle={styles.scrollContent}>
        <Text style={styles.label}>First Name</Text>
        <TextInput
          style={styles.input}
          placeholder="Enter first name"
          placeholderTextColor="#8892b0"
          value={formData.first_name}
          onChangeText={(text) => setFormData({ ...formData, first_name: text })}
        />

        <Text style={styles.label}>Last Name</Text>
        <TextInput
          style={styles.input}
          placeholder="Enter last name"
          placeholderTextColor="#8892b0"
          value={formData.last_name}
          onChangeText={(text) => setFormData({ ...formData, last_name: text })}
        />

        <Text style={styles.sectionTitle}>Emergency Contact</Text>

        <Text style={styles.label}>Name</Text>
        <TextInput
          style={styles.input}
          placeholder="Emergency contact name"
          placeholderTextColor="#8892b0"
          value={formData.emergency_contact_name}
          onChangeText={(text) => setFormData({ ...formData, emergency_contact_name: text })}
        />

        <Text style={styles.label}>Phone Number</Text>
        <TextInput
          style={styles.input}
          placeholder="+1 (555) 123-4567"
          placeholderTextColor="#8892b0"
          value={formData.emergency_contact_phone}
          onChangeText={(text) => setFormData({ ...formData, emergency_contact_phone: text })}
          keyboardType="phone-pad"
        />

        <Text style={styles.sectionTitle}>Health Notes</Text>

        <TextInput
          style={[styles.input, styles.textArea]}
          placeholder="Any health notes or concerns you'd like to share..."
          placeholderTextColor="#8892b0"
          value={formData.health_notes}
          onChangeText={(text) => setFormData({ ...formData, health_notes: text })}
          multiline
          numberOfLines={4}
          textAlignVertical="top"
        />

        <TouchableOpacity
          style={[styles.saveButton, isSaving && styles.saveButtonDisabled]}
          onPress={handleSave}
          disabled={isSaving}
        >
          {isSaving ? (
            <ActivityIndicator color="#1a1a2e" />
          ) : (
            <Text style={styles.saveButtonText}>Save Changes</Text>
          )}
        </TouchableOpacity>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: '#1a1a2e',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#0f3460',
  },
  backButton: {
    padding: 4,
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#ffffff',
  },
  container: {
    flex: 1,
  },
  scrollContent: {
    padding: 20,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#ffffff',
    marginTop: 24,
    marginBottom: 16,
  },
  label: {
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
  textArea: {
    height: 120,
    paddingTop: 16,
  },
  saveButton: {
    backgroundColor: '#64ffda',
    borderRadius: 12,
    padding: 18,
    alignItems: 'center',
    marginTop: 32,
    marginBottom: 40,
  },
  saveButtonDisabled: {
    opacity: 0.6,
  },
  saveButtonText: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1a1a2e',
  },
});
