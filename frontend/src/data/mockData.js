export const PRASHANTH_BRANCHES = [
  { id: 'b1', code: 'KOL', name: 'Kolathur (Call Center Hub)', city: 'Chennai North', status: 'ACTIVE', type: 'HOSPITAL', leadsToday: 142 },
  { id: 'b2', code: 'CHP', name: 'Chetpet', city: 'Central Chennai', status: 'ACTIVE', type: 'HOSPITAL', leadsToday: 98 },
  { id: 'b3', code: 'VEL', name: 'Velachery', city: 'Chennai South', status: 'ACTIVE', type: 'HOSPITAL', leadsToday: 115 },
  { id: 'b4', code: 'GUM', name: 'Gummidipoondi', city: 'Tiruvallur Suburbs', status: 'ACTIVE', type: 'HOSPITAL', leadsToday: 46 },
  { id: 'b5', code: 'GUD', name: 'Guduvanchery', city: 'Chennai South Suburbs', status: 'UPCOMING', type: 'HOSPITAL', leadsToday: 0 },
  { id: 'b6', code: 'NAV', name: 'Navalur', city: 'OMR IT Corridor', status: 'UPCOMING', type: 'HOSPITAL', leadsToday: 0 },
  { id: 'b7', code: 'IVF', name: 'IVF Clinics Network', city: 'Multi-location', status: 'ACTIVE', type: 'FERTILITY', leadsToday: 54 },
];

export const MOCK_ENQUIRIES = [
  {
    id: 'ENQ-2026-8801',
    patientName: 'Karthik Raja',
    phone: '+91 98401 54321',
    age: 48,
    gender: 'Male',
    branch: 'Kolathur (Call Center Hub)',
    department: 'Cardiology',
    doctorName: 'Dr. S. Prashanth, Sr. Cardiologist',
    enquiryType: 'Coronary Angiogram Inquiry',
    priority: 'HIGH',
    status: 'SURGERY_FIXED',
    disposition: 'APPOINTMENT_FIXED',
    assignedSLM: 'Vijay Kumar (SLM Cardio)',
    timeAgo: '12 mins ago',
    audioDuration: '2m 14s',
    recordingUrl: 'wav_8801.wav', // Available voice path
    remarks: 'Patient reports mild exertional chest pain. Fixed procedure appointment for Thursday 10:00 AM.',
    fcmBypassed: false
  },
  {
    id: 'ENQ-2026-8802',
    patientName: 'Meenakshi Sundaram',
    phone: '+91 94440 12890',
    age: 34,
    gender: 'Female',
    branch: 'Chetpet',
    department: 'IVF & Fertility',
    doctorName: 'Dr. Geetha Haripriya, Lead Fertility Specialist',
    enquiryType: 'General IVF Pricing & Package Inquiry', // Broad SLM query type
    priority: 'URGENT',
    status: 'APPOINTMENT_CONFIRMED',
    disposition: 'INFO_GIVEN',
    assignedSLM: 'Anitha Ramesh (SLM Fertility)',
    timeAgo: '28 mins ago',
    audioDuration: null,
    recordingUrl: null, // Nullable voice path (audio sync pending)
    remarks: 'Shared 3rd cycle tariff estimate via WhatsApp. Scheduled in-person counseling on Friday 11:30 AM.',
    fcmBypassed: false
  },
  {
    id: 'ENQ-2026-8803',
    patientName: 'Srinivasan K.',
    phone: '+91 98841 00112',
    age: 52,
    gender: 'Male',
    branch: 'Velachery',
    department: 'General Services',
    doctorName: 'N/A (Agent FCR)',
    enquiryType: 'OPD Timing & Specialist Availability Request', // General Info Request
    priority: 'MEDIUM',
    status: 'CLOSED', // First-Contact Resolution (FCR)
    disposition: 'INFO_GIVEN',
    assignedSLM: 'None (FCR Agent Resolved)',
    timeAgo: '35 mins ago',
    audioDuration: null,
    recordingUrl: null,
    remarks: 'Call Center Agent provided OPD timings for Velachery branch over phone. Query resolved immediately.',
    fcmBypassed: true // FCM push suppressed
  },
  {
    id: 'ENQ-2026-8804',
    patientName: 'Subramanian V.',
    phone: '+91 98840 98765',
    age: 62,
    gender: 'Male',
    branch: 'Velachery',
    department: 'Orthopedics',
    doctorName: 'Dr. R. Balaji, Knee Replacement Specialist',
    enquiryType: 'Bilateral Knee Surgery Estimate',
    priority: 'HIGH',
    status: 'DOCTOR_CONSULTED',
    disposition: 'ESTIMATE_PROVIDED',
    assignedSLM: 'Suresh Babu (SLM Ortho)',
    timeAgo: '45 mins ago',
    audioDuration: '3m 40s',
    recordingUrl: 'wav_8803.wav',
    remarks: 'Reviewed X-ray scans with Dr. Balaji. Shared package estimate.',
    fcmBypassed: false
  }
];
