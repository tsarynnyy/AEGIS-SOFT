"""
Seed demo data for Aegis AI platform.
Creates synthetic member profiles with realistic health metrics.
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timedelta
import random
import os
from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]


async def clear_collections():
    """Clear existing data"""
    print("Clearing existing collections...")
    await db.users.delete_many({})
    await db.members.delete_many({})
    await db.metric_samples.delete_many({})
    await db.risk_events.delete_many({})
    await db.consents.delete_many({})
    await db.device_accounts.delete_many({})
    print("Collections cleared")


async def create_demo_organization():
    """Create demo organization"""
    org_data = {
        'id': 'demo-org-001',
        'name': 'Demo Wellness Organization',
        'timezone': 'Europe/Kyiv',
        'locale': 'en-US',
        'risk_sensitivity': 'medium',
        'hipaa_enabled': True,
        'gdpr_enabled': True,
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow()
    }
    await db.organizations.insert_one(org_data)
    print(f"Created organization: {org_data['name']}")
    return org_data['id']


async def create_demo_members(org_id: str):
    """Create 10 demo member profiles with varied health patterns"""
    members_data = [
        {
            'id': f'member-{i:03d}',
            'user_id': f'user-{i:03d}',
            'org_id': org_id,
            'first_name': first_names[i % len(first_names)],
            'last_name': last_names[i % len(last_names)],
            'date_of_birth': (datetime.now() - timedelta(days=365*random.randint(65, 85))).date(),
            'locale': 'en-US',
            'timezone': 'Europe/Kyiv',
            'data_sharing_enabled': True,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        for i in range(10)
    ]
    
    # Create users first
    for i, member in enumerate(members_data):
        user_data = {
            'id': member['user_id'],
            'email': f"demo.member{i}@aegis-demo.com",
            'hashed_password': "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5yvVF9jqYqxqO",  # "demo123"
            'role': 'member',
            'first_name': member['first_name'],
            'last_name': member['last_name'],
            'is_active': True,
            'is_verified': True,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        await db.users.insert_one(user_data)
    
    # Insert members
    for member in members_data:
        # Convert date_of_birth to datetime for MongoDB
        member_copy = member.copy()
        member_copy['date_of_birth'] = datetime.combine(member['date_of_birth'], datetime.min.time())
        await db.members.insert_one(member_copy)
    
    print(f"Created {len(members_data)} demo members")
    return members_data


async def generate_health_metrics(member_id: str, pattern: str):
    """Generate realistic health metrics for a member based on pattern"""
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=30)
    
    metrics = []
    
    # Generate daily metrics for 30 days
    for day in range(30):
        date = start_date + timedelta(days=day)
        
        # Base values
        if pattern == "healthy":
            hrv_base = random.uniform(50, 65)
            sleep_eff_base = random.uniform(0.82, 0.92)
            steps_base = random.randint(6000, 10000)
        elif pattern == "declining_hrv":
            # HRV declining over time
            hrv_base = random.uniform(55, 65) - (day * 0.8)
            sleep_eff_base = random.uniform(0.78, 0.88)
            steps_base = random.randint(5000, 8000)
        elif pattern == "poor_sleep":
            hrv_base = random.uniform(48, 58)
            # Poor sleep most nights
            sleep_eff_base = random.uniform(0.60, 0.75) if random.random() > 0.3 else random.uniform(0.80, 0.85)
            steps_base = random.randint(4000, 7000)
        elif pattern == "low_activity":
            hrv_base = random.uniform(45, 55)
            sleep_eff_base = random.uniform(0.75, 0.85)
            # Declining activity
            steps_base = random.randint(7000, 9000) - (day * 80)
        else:  # mixed_concerns
            hrv_base = random.uniform(48, 58) - (day * 0.5)
            sleep_eff_base = random.uniform(0.65, 0.75)
            steps_base = random.randint(5000, 8000) - (day * 50)
        
        # HRV
        metrics.append({
            'id': f"{member_id}-hrv-{day}",
            'member_id': member_id,
            'type': 'hrv',
            'value_num': max(30, hrv_base + random.uniform(-3, 3)),
            'unit': 'ms',
            'source': 'mock',
            'timestamp': date,
            'ingested_at': datetime.utcnow()
        })
        
        # Sleep Efficiency
        metrics.append({
            'id': f"{member_id}-sleep-{day}",
            'member_id': member_id,
            'type': 'sleep_efficiency',
            'value_num': max(0.5, min(1.0, sleep_eff_base + random.uniform(-0.05, 0.05))),
            'unit': 'ratio',
            'source': 'mock',
            'timestamp': date,
            'ingested_at': datetime.utcnow()
        })
        
        # Steps
        metrics.append({
            'id': f"{member_id}-steps-{day}",
            'member_id': member_id,
            'type': 'steps',
            'value_num': max(1000, int(steps_base + random.randint(-500, 500))),
            'unit': 'steps',
            'source': 'mock',
            'timestamp': date,
            'ingested_at': datetime.utcnow()
        })
        
        # Heart Rate
        metrics.append({
            'id': f"{member_id}-hr-{day}",
            'member_id': member_id,
            'type': 'heart_rate',
            'value_num': random.randint(60, 85),
            'unit': 'bpm',
            'source': 'mock',
            'timestamp': date,
            'ingested_at': datetime.utcnow()
        })
        
        # Weight (weekly)
        if day % 7 == 0:
            metrics.append({
                'id': f"{member_id}-weight-{day}",
                'member_id': member_id,
                'type': 'weight',
                'value_num': random.uniform(65, 85),
                'unit': 'kg',
                'source': 'mock',
                'timestamp': date,
                'ingested_at': datetime.utcnow()
            })
    
    # Insert metrics
    if metrics:
        await db.metric_samples.insert_many(metrics)
    
    return len(metrics)


async def seed_data():
    """Main seeding function"""
    print("=" * 60)
    print("Aegis AI - Seeding Demo Data")
    print("=" * 60)
    
    # Clear existing data
    await clear_collections()
    
    # Create organization
    org_id = await create_demo_organization()
    
    # Create members
    members = await create_demo_members(org_id)
    
    # Health patterns
    patterns = [
        "healthy",
        "healthy",
        "healthy",
        "declining_hrv",
        "declining_hrv",
        "poor_sleep",
        "poor_sleep",
        "low_activity",
        "mixed_concerns",
        "mixed_concerns"
    ]
    
    # Generate metrics for each member
    print("\nGenerating health metrics...")
    total_metrics = 0
    for i, member in enumerate(members):
        pattern = patterns[i]
        count = await generate_health_metrics(member['id'], pattern)
        total_metrics += count
        print(f"  {member['first_name']} {member['last_name']}: {count} metrics ({pattern})")
    
    # Create device connections
    print("\nCreating device connections...")
    for member in members:
        device_data = {
            'id': f"device-{member['id']}",
            'member_id': member['id'],
            'device_type': 'mock',
            'device_name': 'Demo Health Tracker',
            'is_active': True,
            'last_sync_at': datetime.utcnow(),
            'last_sync_status': 'success',
            'connected_at': datetime.utcnow() - timedelta(days=30),
            'updated_at': datetime.utcnow()
        }
        await db.device_accounts.insert_one(device_data)
    
    print(f"Created {len(members)} device connections")
    
    # Create consents
    print("\nCreating consents...")
    consent_types = ['data_collection', 'data_sharing', 'caregiver_access']
    for member in members:
        for consent_type in consent_types:
            consent_data = {
                'id': f"consent-{member['id']}-{consent_type}",
                'member_id': member['id'],
                'consent_type': consent_type,
                'granted': True,
                'version': '1.0',
                'source': 'onboarding',
                'granted_at': datetime.utcnow() - timedelta(days=30)
            }
            await db.consents.insert_one(consent_data)
    
    print(f"Created {len(members) * len(consent_types)} consents")
    
    print("\n" + "=" * 60)
    print("Demo data seeded successfully!")
    print("=" * 60)
    print(f"\nSummary:")
    print(f"  - Organization: 1")
    print(f"  - Members: {len(members)}")
    print(f"  - Health Metrics: {total_metrics}")
    print(f"  - Device Connections: {len(members)}")
    print(f"  - Consents: {len(members) * len(consent_types)}")
    print(f"\nDemo credentials:")
    print(f"  Email: demo.member0@aegis-demo.com to demo.member9@aegis-demo.com")
    print(f"  Password: demo123")
    print("=" * 60)
    
    client.close()


# Demo names
first_names = ["John", "Mary", "Robert", "Patricia", "Michael", "Jennifer", "William", "Linda", "David", "Barbara"]
last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"]


if __name__ == "__main__":
    asyncio.run(seed_data())
