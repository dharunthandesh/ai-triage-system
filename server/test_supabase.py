from supabase_client import supabase

# Insert test patient
insert_response = supabase.table("patients").insert({
    "name": "Dharun",
    "phone": "9876543210",
    "password": "1234"
}).execute()

print("Inserted:", insert_response.data)

# Fetch all patients
response = supabase.table("patients").select("*").execute()

print("All Patients:", response.data)
