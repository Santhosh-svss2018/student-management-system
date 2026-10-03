// Central Static Mock Data for EduManage Frontend UI (No fake API calls)

export const MOCK_STATS = {
  admin: [
    { label: 'Total Enrolled Students', value: '4,850', change: '+8.4%', trend: 'up', period: 'vs last semester', color: 'primary' },
    { label: 'Active Faculty Members', value: '248', change: '+3 new', trend: 'up', period: 'this academic year', color: 'tertiary' },
    { label: 'Average Attendance', value: '92.4%', change: '+1.8%', trend: 'up', period: 'across all depts', color: 'secondary' },
    { label: 'Fee Collection Rate', value: '94.2%', change: '+4.1%', trend: 'up', period: '$2.84M collected', color: 'primary' },
  ],
  teacher: [
    { label: 'Assigned Classes', value: '4 Courses', change: '18 hrs/wk', trend: 'neutral', period: 'Semester 6', color: 'primary' },
    { label: 'Total Students', value: '210', change: 'across 3 batches', trend: 'neutral', period: 'CS & IT', color: 'secondary' },
    { label: 'Class Avg. Attendance', value: '89.6%', change: '-0.8%', trend: 'down', period: 'last 30 days', color: 'tertiary' },
    { label: 'Pending Evaluations', value: '38 Submissions', change: 'Due in 2 days', trend: 'alert', period: 'Mid-term Lab', color: 'error' },
  ],
  student: [
    { label: 'Cumulative GPA (CGPA)', value: '8.84', change: 'Top 5%', trend: 'up', period: 'Out of 10.0', color: 'primary' },
    { label: 'Overall Attendance', value: '94.2%', change: 'Safe zone', trend: 'up', period: 'Min required: 75%', color: 'tertiary' },
    { label: 'Credits Completed', value: '112 / 160', change: '70% done', trend: 'neutral', period: 'Semester 6', color: 'secondary' },
    { label: 'Upcoming Deadlines', value: '2 Exams, 1 Lab', change: 'Next: 3 days', trend: 'neutral', period: 'Midterm exams', color: 'primary' },
  ]
};

export const MOCK_STUDENTS = [
  {
    id: 'STU-2022-089',
    rollNo: 'CS-22-089',
    name: 'Arun Kumar',
    email: 'arun.kumar@student.edumanage.edu',
    phone: '+91 98765 43210',
    department: 'Computer Science & Engineering',
    semester: '6th Semester',
    batch: '2022 - 2026',
    section: 'CS-A',
    cgpa: 8.84,
    attendance: 94.2,
    status: 'Active',
    riskLevel: 'Low',
    avatar: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&auto=format&fit=crop&q=80',
    guardian: {
      name: 'Rajesh Kumar',
      relation: 'Father',
      phone: '+91 98450 12345',
      email: 'rajesh.k@gmail.com',
      occupation: 'Civil Engineer'
    },
    address: '42 Orchid Heights, Indiranagar, Bengaluru, KA 560038',
    dob: '2004-05-14',
    bloodGroup: 'O+'
  },
  {
    id: 'STU-2022-090',
    rollNo: 'CS-22-090',
    name: 'Priya Sharma',
    email: 'priya.sharma@student.edumanage.edu',
    phone: '+91 98112 34567',
    department: 'Computer Science & Engineering',
    semester: '6th Semester',
    batch: '2022 - 2026',
    section: 'CS-A',
    cgpa: 9.25,
    attendance: 98.0,
    status: 'Active',
    riskLevel: 'Low',
    avatar: 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=150&auto=format&fit=crop&q=80',
    guardian: { name: 'Sunita Sharma', relation: 'Mother', phone: '+91 98112 99999' },
    address: '15 Lotus Boulevard, Whitefield, Bengaluru',
    dob: '2004-02-18',
    bloodGroup: 'B+'
  },
  {
    id: 'STU-2022-091',
    rollNo: 'CS-22-091',
    name: 'Rohan Mehta',
    email: 'rohan.mehta@student.edumanage.edu',
    phone: '+91 97654 32109',
    department: 'Information Technology',
    semester: '6th Semester',
    batch: '2022 - 2026',
    section: 'IT-B',
    cgpa: 6.72,
    attendance: 68.5,
    status: 'At Risk',
    riskLevel: 'High',
    avatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&auto=format&fit=crop&q=80',
    guardian: { name: 'Anil Mehta', relation: 'Father', phone: '+91 97654 88888' },
    address: '88 Palm Grove, Koramangala, Bengaluru',
    dob: '2003-11-29',
    bloodGroup: 'A+'
  },
  {
    id: 'STU-2022-092',
    rollNo: 'CS-22-092',
    name: 'Ananya Roy',
    email: 'ananya.roy@student.edumanage.edu',
    phone: '+91 99234 56789',
    department: 'Electronics & Communication',
    semester: '4th Semester',
    batch: '2023 - 2027',
    section: 'EC-A',
    cgpa: 8.40,
    attendance: 91.0,
    status: 'Active',
    riskLevel: 'Low',
    avatar: 'https://images.unsplash.com/photo-1517841905240-472988babdf9?w=150&auto=format&fit=crop&q=80',
    guardian: { name: 'Debashis Roy', relation: 'Father', phone: '+91 99234 11111' },
    address: '102 Green Glen Layout, Bellandur, Bengaluru',
    dob: '2005-01-10',
    bloodGroup: 'AB+'
  },
  {
    id: 'STU-2022-093',
    rollNo: 'CS-22-093',
    name: 'Vikram Malhotra',
    email: 'vikram.m@student.edumanage.edu',
    phone: '+91 98334 56712',
    department: 'Mechanical Engineering',
    semester: '8th Semester',
    batch: '2021 - 2025',
    section: 'ME-A',
    cgpa: 7.65,
    attendance: 82.4,
    status: 'Active',
    riskLevel: 'Medium',
    avatar: 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=150&auto=format&fit=crop&q=80',
    guardian: { name: 'Kiran Malhotra', relation: 'Father', phone: '+91 98334 00000' },
    address: '54 HSR Layout Sector 2, Bengaluru',
    dob: '2003-08-04',
    bloodGroup: 'O-'
  },
  {
    id: 'STU-2022-094',
    rollNo: 'CS-22-094',
    name: 'Sneha Patel',
    email: 'sneha.patel@student.edumanage.edu',
    phone: '+91 97123 45678',
    department: 'Computer Science & Engineering',
    semester: '6th Semester',
    batch: '2022 - 2026',
    section: 'CS-B',
    cgpa: 8.90,
    attendance: 95.8,
    status: 'Active',
    riskLevel: 'Low',
    avatar: 'https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=150&auto=format&fit=crop&q=80',
    guardian: { name: 'Bhavesh Patel', relation: 'Father', phone: '+91 97123 99999' },
    address: '77 JP Nagar Phase 5, Bengaluru',
    dob: '2004-09-22',
    bloodGroup: 'A+'
  },
  {
    id: 'STU-2022-095',
    rollNo: 'CS-22-095',
    name: 'Karthik Raman',
    email: 'karthik.r@student.edumanage.edu',
    phone: '+91 96543 21876',
    department: 'Civil Engineering',
    semester: '6th Semester',
    batch: '2022 - 2026',
    section: 'CE-A',
    cgpa: 6.95,
    attendance: 71.2,
    status: 'At Risk',
    riskLevel: 'High',
    avatar: 'https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=150&auto=format&fit=crop&q=80',
    guardian: { name: 'S. Ramanathan', relation: 'Father', phone: '+91 96543 55555' },
    address: '33 Malleshwaram 18th Cross, Bengaluru',
    dob: '2004-04-12',
    bloodGroup: 'B+'
  },
  {
    id: 'STU-2022-096',
    rollNo: 'CS-22-096',
    name: 'Divya Nair',
    email: 'divya.nair@student.edumanage.edu',
    phone: '+91 95432 10987',
    department: 'Computer Science & Engineering',
    semester: '6th Semester',
    batch: '2022 - 2026',
    section: 'CS-A',
    cgpa: 9.10,
    attendance: 96.5,
    status: 'Active',
    riskLevel: 'Low',
    avatar: 'https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=150&auto=format&fit=crop&q=80',
    guardian: { name: 'Nandakumar Nair', relation: 'Father', phone: '+91 95432 44444' },
    address: '19 Bannerghatta Main Road, Bengaluru',
    dob: '2004-07-30',
    bloodGroup: 'O+'
  }
];

export const MOCK_COURSES = [
  { id: 'CS-301', code: 'CS-301', title: 'Design & Analysis of Algorithms', instructor: 'Prof. Marcus Vance', credits: 4, schedule: 'Mon, Wed, Fri 10:00 AM', room: 'LH-302', studentsCount: 64, attendance: 92 },
  { id: 'CS-302', code: 'CS-302', title: 'Database Management Systems', instructor: 'Dr. Anita Desai', credits: 4, schedule: 'Tue, Thu 11:30 AM', room: 'LH-105', studentsCount: 68, attendance: 88 },
  { id: 'CS-303', code: 'CS-303', title: 'Operating Systems & Concurrency', instructor: 'Prof. Kevin Taylor', credits: 3, schedule: 'Mon, Wed 02:00 PM', room: 'LH-201', studentsCount: 62, attendance: 94 },
  { id: 'CS-304', code: 'CS-304', title: 'Computer Networks & Security', instructor: 'Dr. Sarah Jenkins', credits: 4, schedule: 'Tue, Thu, Fri 09:00 AM', room: 'LH-401', studentsCount: 59, attendance: 90 },
  { id: 'CS-305', code: 'CS-305', title: 'Artificial Intelligence & ML', instructor: 'Dr. Robert Chen', credits: 3, schedule: 'Wed, Fri 03:30 PM', room: 'AI-Lab 2', studentsCount: 55, attendance: 96 }
];

export const MOCK_FACULTY = [
  {
    id: 'FAC-104',
    name: 'Prof. Marcus Vance',
    email: 'marcus.vance@edumanage.edu',
    phone: '+91 94432 10987',
    department: 'Computer Science & Engineering',
    designation: 'Associate Professor',
    specialization: 'Distributed Systems & Advanced Algorithms',
    cabin: 'Room 408, CS Block B',
    joiningDate: '2016-08-15',
    experience: '12+ Years',
    avatar: 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150&auto=format&fit=crop&q=80',
    assignedCourses: ['CS-301: Design & Analysis of Algorithms', 'CS-402: Cloud Architecture & DevOps'],
    publications: 18,
    activeProjects: 3
  }
];

export const MOCK_ATTENDANCE_RECORDS = [
  { id: 1, rollNo: 'CS-22-089', name: 'Arun Kumar', status: 'Present', time: '09:58 AM' },
  { id: 2, rollNo: 'CS-22-090', name: 'Priya Sharma', status: 'Present', time: '09:55 AM' },
  { id: 3, rollNo: 'CS-22-091', name: 'Rohan Mehta', status: 'Absent', time: '-' },
  { id: 4, rollNo: 'CS-22-092', name: 'Ananya Roy', status: 'Present', time: '10:01 AM' },
  { id: 5, rollNo: 'CS-22-093', name: 'Vikram Malhotra', status: 'Late', time: '10:14 AM' },
  { id: 6, rollNo: 'CS-22-094', name: 'Sneha Patel', status: 'Present', time: '09:52 AM' },
  { id: 7, rollNo: 'CS-22-095', name: 'Karthik Raman', status: 'Absent', time: '-' },
  { id: 8, rollNo: 'CS-22-096', name: 'Divya Nair', status: 'Present', time: '09:50 AM' },
];

export const MOCK_MARKS_RECORDS = [
  { id: 1, rollNo: 'CS-22-089', name: 'Arun Kumar', quiz1: 18, midterm: 44, assignment: 28, practical: 48, total: 138, max: 150, grade: 'A+', status: 'Submitted' },
  { id: 2, rollNo: 'CS-22-090', name: 'Priya Sharma', quiz1: 20, midterm: 48, assignment: 30, practical: 50, total: 148, max: 150, grade: 'O', status: 'Submitted' },
  { id: 3, rollNo: 'CS-22-091', name: 'Rohan Mehta', quiz1: 11, midterm: 26, assignment: 18, practical: 32, total: 87, max: 150, grade: 'C', status: 'Draft' },
  { id: 4, rollNo: 'CS-22-092', name: 'Ananya Roy', quiz1: 17, midterm: 42, assignment: 27, practical: 44, total: 130, max: 150, grade: 'A', status: 'Submitted' },
  { id: 5, rollNo: 'CS-22-093', name: 'Vikram Malhotra', quiz1: 14, midterm: 35, assignment: 22, practical: 38, total: 109, max: 150, grade: 'B+', status: 'Submitted' },
  { id: 6, rollNo: 'CS-22-094', name: 'Sneha Patel', quiz1: 19, midterm: 45, assignment: 29, practical: 47, total: 140, max: 150, grade: 'A+', status: 'Submitted' },
  { id: 7, rollNo: 'CS-22-095', name: 'Karthik Raman', quiz1: 10, midterm: 24, assignment: 19, practical: 30, total: 83, max: 150, grade: 'C', status: 'Draft' },
  { id: 8, rollNo: 'CS-22-096', name: 'Divya Nair', quiz1: 19, midterm: 46, assignment: 29, practical: 49, total: 143, max: 150, grade: 'O', status: 'Submitted' },
];

export const MOCK_AI_INSIGHTS = [
  {
    id: 'INS-01',
    type: 'High Risk Alert',
    student: 'Rohan Mehta (CS-22-091)',
    category: 'Attendance & Assignment Deficit',
    description: 'Attendance declined from 84% to 68.5% over the past 3 weeks. Missed 2 consecutive Algorithms lab submissions.',
    recommendation: 'Trigger academic counselor meeting and notify batch faculty advisor.',
    severity: 'High',
    probability: '82% Dropout/Detention Risk'
  },
  {
    id: 'INS-02',
    type: 'Academic Performance Drop',
    student: 'Karthik Raman (CS-22-095)',
    category: 'Midterm Marks Deviation',
    description: 'Scored 24/50 in DBMS midterm compared to a batch average of 39.4/50.',
    recommendation: 'Recommend peer tutoring group and remedial tutorial sessions for SQL indexing module.',
    severity: 'Medium',
    probability: '65% Backlog Probability'
  },
  {
    id: 'INS-03',
    type: 'Exceptional Performance',
    student: 'Priya Sharma (CS-22-090)',
    category: 'Dean\'s Honor List Eligible',
    description: 'Maintained 9.25 CGPA with 98% attendance. Eligible for IEEE conference sponsorship and research fellowship.',
    recommendation: 'Forward application for University Merit Scholarship Phase 2.',
    severity: 'Low',
    probability: 'Top 1% Percentile'
  }
];

export const MOCK_CHAT_PROMPTS = [
  { label: 'Summarize Discrete Math Chapter 4', icon: 'BookOpen' },
  { label: 'Check my current attendance eligibility for finals', icon: 'CheckCircle' },
  { label: 'Generate a 2-week study plan for Midterms', icon: 'Calendar' },
  { label: 'Explain Dijkstra\'s Algorithm with time complexity', icon: 'Code' }
];

export const MOCK_CHAT_HISTORY = [
  {
    id: 1,
    sender: 'ai',
    message: 'Hello Arun! I am EduAI, your personal academic assistant. How can I help you today with your courses, timetable, or exam preparations?',
    time: '10:30 AM'
  },
  {
    id: 2,
    sender: 'user',
    message: 'Can you summarize my academic status for the 6th semester so far?',
    time: '10:32 AM'
  },
  {
    id: 3,
    sender: 'ai',
    message: 'Here is your 6th Semester snapshot:\n\n• **CGPA**: **8.84** (Strong distinction)\n• **Overall Attendance**: **94.2%** (Well above 75% threshold)\n• **Highest Performing Course**: CS-301 Design & Analysis of Algorithms (92%)\n• **Upcoming Deadline**: CS-302 DBMS Lab Submission in 3 days.\n\nKeep up the great momentum! Would you like practice questions for your upcoming Algorithms midterm?',
    time: '10:32 AM'
  }
];

export const MOCK_ACTIVITIES = [
  { id: 1, title: 'Attendance Marked', desc: 'Prof. Marcus Vance marked attendance for CS-301 (6th Sem)', time: '10 mins ago', type: 'attendance' },
  { id: 2, title: 'Midterm Marks Published', desc: 'Dr. Anita Desai published results for CS-302', time: '1 hour ago', type: 'marks' },
  { id: 3, title: 'New Student Enrolled', desc: 'Admissions office registered 12 transfer students', time: '3 hours ago', type: 'student' },
  { id: 4, title: 'System Backup Complete', desc: 'Institutional cloud database synced successfully', time: '5 hours ago', type: 'system' }
];
