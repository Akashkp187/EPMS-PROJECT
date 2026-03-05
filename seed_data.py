"""
Demo seed data: departments, employees per department (12 each), job titles, goal/review/feedback templates.
Used by run.seed() to populate a rich demo database.
"""
from datetime import date, datetime, timedelta

# ---------------------------------------------------------------------------
# Departments: name, code, description, image_url
# ---------------------------------------------------------------------------
DEPARTMENTS = [
    ("Engineering", "ENG", "Software and product engineering", "https://images.unsplash.com/photo-1518770660439-4636190af475?w=800"),
    ("Human Resources", "HR", "People and culture", "https://images.unsplash.com/photo-1552664730-d307ca884978?w=800"),
    ("Operations", "OPS", "Business operations", "https://images.unsplash.com/photo-1520607162513-77705c0f0d4a?w=800"),
    ("Finance", "FIN", "Financial planning and analysis", "https://images.unsplash.com/photo-1554224155-6726b3ff858f?w=800"),
    ("Sales", "SAL", "Revenue and customer relationships", "https://images.unsplash.com/photo-1521737604893-d14cc237f11d?w=800"),
    ("Marketing", "MKT", "Brand, campaigns and growth", "https://images.unsplash.com/photo-1553877522-43269d4ea984?w=800"),
    ("IT Support", "ITS", "Internal IT and support", "https://images.unsplash.com/photo-1517245386807-bb43f82c33c4?w=800"),
    ("Product", "PRD", "Product strategy and roadmap", "https://images.unsplash.com/photo-1551434678-e076c223a692?w=800"),
    ("Customer Success", "CUS", "Customer onboarding and retention", "https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?w=800"),
    ("Design", "DSN", "UX, UI and design systems", "https://images.unsplash.com/photo-1561070791-2526d30994b5?w=800"),
]

# ---------------------------------------------------------------------------
# Manager per department: (email_suffix, username_suffix, first_name, last_name, job_title)
# ---------------------------------------------------------------------------
MANAGERS = [
    ("eng.manager", "Ananya", "Iyer", "Engineering Manager"),
    ("hr.manager", "Priya", "Sharma", "HR Manager"),
    ("ops.manager", "Arjun", "Nair", "Operations Manager"),
    ("fin.manager", "Rahul", "Verma", "Finance Manager"),
    ("sales.manager", "Kavya", "Patel", "Sales Manager"),
    ("mkt.manager", "Vikram", "Singh", "Marketing Manager"),
    ("its.manager", "Sneha", "Rao", "IT Support Manager"),
    ("prd.manager", "Kiran", "Bose", "Head of Product"),
    ("cus.manager", "Divya", "Menon", "Customer Success Manager"),
    ("dsn.manager", "Rohan", "Kumar", "Design Manager"),
]

# ---------------------------------------------------------------------------
# Employees per department: 12 each. (email_local, username, first_name, last_name, job_title)
# dept prefix: eng, hr, ops, fin, sales, mkt, its, prd, cus, dsn
# ---------------------------------------------------------------------------
DEPT_PREFIXES = ["eng", "hr", "ops", "fin", "sales", "mkt", "its", "prd", "cus", "dsn"]

EMPLOYEES_BY_DEPT = [
    # Engineering (12)
    [
        ("sahil.dev", "Sahil", "Kulkarni", "Software Engineer"),
        ("meera.dev", "Meera", "Reddy", "Backend Engineer"),
        ("arjun.eng", "Arjun", "Deshmukh", "Frontend Developer"),
        ("pooja.eng", "Pooja", "Nair", "DevOps Engineer"),
        ("raj.eng", "Raj", "Iyer", "Full Stack Developer"),
        ("kavitha.eng", "Kavitha", "Pillai", "QA Engineer"),
        ("vivek.eng", "Vivek", "Sharma", "Software Engineer"),
        ("anita.eng", "Anita", "Gupta", "Tech Lead"),
        ("suresh.eng", "Suresh", "Menon", "Backend Engineer"),
        ("deepa.eng", "Deepa", "Krishnan", "Mobile Developer"),
        ("mohit.eng", "Mohit", "Reddy", "Software Engineer"),
        ("lakshmi.eng", "Lakshmi", "Venkatesh", "SDET"),
    ],
    # HR (12)
    [
        ("lata.hr", "Lata", "Banerjee", "HR Specialist"),
        ("manoj.hr", "Manoj", "Chopra", "People Partner"),
        ("priyanka.hr", "Priyanka", "Nair", "Recruiter"),
        ("sanjay.hr", "Sanjay", "Mehta", "HR Analyst"),
        ("rekha.hr", "Rekha", "Joshi", "Learning & Development"),
        ("amit.hr", "Amit", "Shah", "Compensation Analyst"),
        ("neelam.hr", "Neelam", "Patel", "HR Coordinator"),
        ("vikram.hr", "Vikram", "Singh", "Talent Acquisition"),
        ("swati.hr", "Swati", "Rao", "HR Business Partner"),
        ("rahul.hr", "Rahul", "Kulkarni", "HR Specialist"),
        ("kirti.hr", "Kirti", "Desai", "People Operations"),
        ("anil.hr", "Anil", "Reddy", "HR Associate"),
    ],
    # Operations (12)
    [
        ("omkar.ops", "Omkar", "Desai", "Operations Analyst"),
        ("isha.ops", "Isha", "Malhotra", "Process Executive"),
        ("nitin.ops", "Nitin", "Sharma", "Supply Chain Analyst"),
        ("preeti.ops", "Preeti", "Gupta", "Operations Coordinator"),
        ("sandeep.ops", "Sandeep", "Nair", "Logistics Specialist"),
        ("divya.ops", "Divya", "Iyer", "Process Improvement Lead"),
        ("manish.ops", "Manish", "Patel", "Operations Executive"),
        ("shalini.ops", "Shalini", "Joshi", "Vendor Manager"),
        ("rohit.ops", "Rohit", "Kumar", "Operations Analyst"),
        ("kavita.ops", "Kavita", "Reddy", "Business Operations"),
        ("ajay.ops", "Ajay", "Mehta", "Operations Specialist"),
        ("pallavi.ops", "Pallavi", "Singh", "Process Analyst"),
    ],
    # Finance (12)
    [
        ("tanya.fin", "Tanya", "Mehta", "Financial Analyst"),
        ("rohan.fin", "Rohan", "Joshi", "Accountant"),
        ("shruti.fin", "Shruti", "Shah", "Senior Accountant"),
        ("akash.fin", "Akash", "Patel", "FP&A Analyst"),
        ("megha.fin", "Megha", "Nair", "Tax Specialist"),
        ("varun.fin", "Varun", "Kumar", "Financial Analyst"),
        ("sonal.fin", "Sonal", "Reddy", "Accounts Payable"),
        ("karan.fin", "Karan", "Gupta", "Treasury Analyst"),
        ("nidhi.fin", "Nidhi", "Iyer", "Financial Reporting"),
        ("aditya.fin", "Aditya", "Deshmukh", "Accountant"),
        ("pooja.fin", "Pooja", "Sharma", "Finance Associate"),
        ("rahul.fin", "Rahul", "Joshi", "Budget Analyst"),
    ],
    # Sales (12)
    [
        ("aditya.sales", "Aditya", "Menon", "Account Executive"),
        ("neha.sales", "Neha", "Das", "Sales Associate"),
        ("rahul.sales", "Rahul", "Kapoor", "Senior Account Executive"),
        ("kriti.sales", "Kriti", "Sharma", "Sales Development Rep"),
        ("vijay.sales", "Vijay", "Nair", "Regional Sales Manager"),
        ("ananya.sales", "Ananya", "Patel", "Account Manager"),
        ("siddharth.sales", "Siddharth", "Reddy", "Sales Executive"),
        ("tanvi.sales", "Tanvi", "Gupta", "Inside Sales"),
        ("arjun.sales", "Arjun", "Iyer", "Enterprise Sales"),
        ("isha.sales", "Isha", "Joshi", "Sales Coordinator"),
        ("rohan.sales", "Rohan", "Kumar", "Account Executive"),
        ("divya.sales", "Divya", "Mehta", "Sales Associate"),
    ],
    # Marketing (12)
    [
        ("riya.mkt", "Riya", "Kapoor", "Marketing Executive"),
        ("arav.mkt", "Arav", "Gupta", "Content Strategist"),
        ("neha.mkt", "Neha", "Sharma", "Digital Marketing Specialist"),
        ("karan.mkt", "Karan", "Nair", "Brand Manager"),
        ("shreya.mkt", "Shreya", "Patel", "Social Media Manager"),
        ("vivek.mkt", "Vivek", "Reddy", "Growth Marketing"),
        ("anchal.mkt", "Anchal", "Iyer", "Content Writer"),
        ("manish.mkt", "Manish", "Joshi", "SEO Specialist"),
        ("kavya.mkt", "Kavya", "Kumar", "Marketing Analyst"),
        ("sahil.mkt", "Sahil", "Desai", "Campaign Manager"),
        ("priya.mkt", "Priya", "Singh", "Marketing Coordinator"),
        ("rohit.mkt", "Rohit", "Gupta", "Demand Generation"),
    ],
    # IT Support (12)
    [
        ("veer.its", "Veer", "Pillai", "Support Engineer"),
        ("anika.its", "Anika", "Sen", "Service Desk Analyst"),
        ("kiran.its", "Kiran", "Bose", "IT Support Specialist"),
        ("madhav.its", "Madhav", "Nair", "Desktop Support"),
        ("sneha.its", "Sneha", "Sharma", "Help Desk Analyst"),
        ("abhishek.its", "Abhishek", "Patel", "Systems Administrator"),
        ("reshma.its", "Reshma", "Reddy", "IT Support Technician"),
        ("gaurav.its", "Gaurav", "Kumar", "Network Support"),
        ("lavanya.its", "Lavanya", "Iyer", "Support Lead"),
        ("pratik.its", "Pratik", "Joshi", "IT Support Engineer"),
        ("deepika.its", "Deepika", "Gupta", "Service Desk Agent"),
        ("nitin.its", "Nitin", "Mehta", "Technical Support"),
    ],
    # Product (12)
    [
        ("akash.prd", "Akash", "Menon", "Product Manager"),
        ("divya.prd", "Divya", "Nair", "Associate Product Manager"),
        ("varun.prd", "Varun", "Sharma", "Product Owner"),
        ("kavya.prd", "Kavya", "Patel", "Senior Product Manager"),
        ("siddharth.prd", "Siddharth", "Reddy", "Product Analyst"),
        ("tanvi.prd", "Tanvi", "Iyer", "Product Manager"),
        ("rohan.prd", "Rohan", "Gupta", "Technical Product Manager"),
        ("shreya.prd", "Shreya", "Joshi", "Product Operations"),
        ("arjun.prd", "Arjun", "Kumar", "Product Lead"),
        ("ananya.prd", "Ananya", "Mehta", "Associate PM"),
        ("vivek.prd", "Vivek", "Singh", "Product Manager"),
        ("pooja.prd", "Pooja", "Desai", "Growth Product Manager"),
    ],
    # Customer Success (12)
    [
        ("neha.cus", "Neha", "Kapoor", "Customer Success Manager"),
        ("rahul.cus", "Rahul", "Shah", "CS Associate"),
        ("kriti.cus", "Kriti", "Nair", "Account Manager"),
        ("vijay.cus", "Vijay", "Patel", "Customer Success Lead"),
        ("shalini.cus", "Shalini", "Reddy", "Onboarding Specialist"),
        ("manish.cus", "Manish", "Gupta", "CSM"),
        ("tanvi.cus", "Tanvi", "Iyer", "Customer Support Lead"),
        ("rohit.cus", "Rohit", "Joshi", "Success Manager"),
        ("divya.cus", "Divya", "Kumar", "Client Success"),
        ("sahil.cus", "Sahil", "Mehta", "CS Analyst"),
        ("kavya.cus", "Kavya", "Singh", "Renewal Manager"),
        ("arjun.cus", "Arjun", "Desai", "CS Associate"),
    ],
    # Design (12)
    [
        ("riya.dsn", "Riya", "Bose", "UX Designer"),
        ("karan.dsn", "Karan", "Nair", "UI Designer"),
        ("shreya.dsn", "Shreya", "Patel", "Product Designer"),
        ("vivek.dsn", "Vivek", "Reddy", "Senior UX Designer"),
        ("anchal.dsn", "Anchal", "Iyer", "Visual Designer"),
        ("siddharth.dsn", "Siddharth", "Gupta", "Design Lead"),
        ("kavya.dsn", "Kavya", "Joshi", "UX Researcher"),
        ("rohan.dsn", "Rohan", "Kumar", "Interaction Designer"),
        ("tanvi.dsn", "Tanvi", "Sharma", "UI/UX Designer"),
        ("arjun.dsn", "Arjun", "Mehta", "Design Systems"),
        ("neha.dsn", "Neha", "Singh", "Product Designer"),
        ("divya.dsn", "Divya", "Desai", "Designer"),
    ],
]

# ---------------------------------------------------------------------------
# Goal templates: (title, description, progress, status, target_offset_days)
# target_offset_days = days from today for target_date (or None)
# ---------------------------------------------------------------------------
GOAL_TEMPLATES = [
    ("Complete quarterly objectives", "Deliver on agreed OKRs for the current quarter. Align with team and stakeholders.", 40, "active", 60),
    ("Attend at least 2 training sessions", "Participate in internal or external upskilling programs and document learnings.", 0, "active", 90),
    ("Improve cross-team collaboration", "Initiate at least one cross-functional project and document outcomes.", 25, "active", 45),
    ("Meet all KPI targets for the period", "Achieve or exceed the agreed KPI targets and report progress monthly.", 60, "active", 30),
    ("Complete certification / course", "Finish one relevant certification or online course and share knowledge with team.", 100, "completed", -30),
    ("Document processes and runbooks", "Create or update documentation for key processes in your area.", 75, "active", 20),
    ("Mentor a junior team member", "Support onboarding or development of at least one colleague.", 50, "active", 75),
]

# ---------------------------------------------------------------------------
# Review content: (summary_template, strengths, improvements)
# Use .format(emp_name=...) for summary
# ---------------------------------------------------------------------------
REVIEW_TEMPLATES = [
    ("Quarterly performance review for {emp_name}. Goals were largely met with strong execution.", "Strong collaboration and ownership. Delivers on commitments.", "Focus on documenting work more consistently. Time management for deep work."),
    ("Mid-year review for {emp_name}. Good progress on technical and soft skills.", "Reliable and proactive. Good communication with stakeholders.", "Prioritization and saying no to scope creep. Technical depth in one area."),
    ("Annual review for {emp_name}. Exceeded expectations in several areas.", "Leadership potential. Customer focus. Quality of deliverables.", "Delegation and mentoring. Strategic thinking and long-term planning."),
]

# ---------------------------------------------------------------------------
# Feedback comments (for peer/manager feedback)
# ---------------------------------------------------------------------------
FEEDBACK_COMMENTS = [
    "Great teamwork on the last project. Always responsive and clear in communication.",
    "Appreciate the detailed documentation and willingness to help others.",
    "Strong problem-solving skills. Would like to see more initiative in leading discussions.",
    "Very reliable and thorough. Could improve on giving concise updates in meetings.",
    "Excellent technical contribution. Consider sharing knowledge in brown-bags.",
]

# ---------------------------------------------------------------------------
# Meeting titles and agendas
# ---------------------------------------------------------------------------
MEETING_TITLES = [
    ("Weekly 1:1", "Progress on goals, blockers, and priorities for next week."),
    ("Performance check-in", "Review of Q2 goals and feedback. Alignment on expectations."),
    ("Career development", "Discussion on growth areas and training opportunities."),
    ("Project sync", "Updates on current projects and resource needs."),
]

# ---------------------------------------------------------------------------
# Training programs: (title, description, provider, duration_hours, status)
# ---------------------------------------------------------------------------
TRAINING_PROGRAMS = [
    ("Leadership Fundamentals", "Core leadership skills for emerging leaders. Covers delegation, feedback, and decision-making.", "Internal", 8.0, "scheduled"),
    ("Performance Improvement", "Structured program to improve goals, feedback, and productivity. Recommended for employees who need additional support.", "Internal", 6.0, "scheduled"),
    ("Advanced Excel & Analytics", "Pivot tables, dashboards, and data analysis for business users.", "Internal", 4.0, "completed"),
    ("Effective Communication", "Written and verbal communication, presentations, and difficult conversations.", "External", 6.0, "scheduled"),
    ("Project Management Basics", "Introduction to PM methodologies, planning, and execution.", "Internal", 8.0, "in_progress"),
    ("Diversity & Inclusion", "Building inclusive teams and unconscious bias awareness.", "External", 3.0, "scheduled"),
    ("Security Awareness", "Data protection, phishing, and safe computing practices.", "Internal", 2.0, "completed"),
    ("Customer Success Best Practices", "Onboarding, retention, and escalation handling.", "Internal", 5.0, "scheduled"),
    ("Agile & Scrum Certification", "Certified Scrum Master prep: ceremonies, backlogs, and sprint planning.", "External", 16.0, "scheduled"),
    ("Data Literacy for Teams", "Reading charts, KPIs, and basic statistics for decision-making.", "Internal", 4.0, "in_progress"),
    ("Time Management & Prioritization", "Eisenhower matrix, deep work, and meeting hygiene.", "Internal", 3.0, "scheduled"),
]

# ---------------------------------------------------------------------------
# KPI definitions per department (by index): (name, description, unit)
# ---------------------------------------------------------------------------
KPI_DEFS = [
    [("Sprint velocity", "Average story points completed per sprint.", "points"), ("Code review turnaround", "Hours to first review on PRs.", "hours"), ("Deployment frequency", "Number of production deployments per week.", "count")],
    [("Employee engagement score", "Overall engagement score from pulse surveys.", "%"), ("Time to hire", "Days from req open to offer accept.", "days"), ("Training completion rate", "Percentage of assigned training completed.", "%")],
    [("Process cycle time", "Average days to complete key processes.", "days"), ("Vendor SLA compliance", "Percentage of SLAs met.", "%"), ("Cost per transaction", "Operational cost per unit.", "currency")],
    [("Budget variance", "Actual vs budget variance.", "%"), ("Report timeliness", "Percentage of reports delivered on time.", "%"), ("Audit findings", "Open audit findings count.", "count")],
    [("Revenue per rep", "Quarterly revenue attributed per sales rep.", "currency"), ("Pipeline conversion", "Opportunity to closed win rate.", "%"), ("New logos", "New customer acquisitions.", "count")],
    [("Campaign ROI", "Return on marketing spend.", "%"), ("Lead quality score", "Average score of marketing-sourced leads.", "score"), ("Brand awareness", "Survey-based brand recall.", "%")],
    [("Ticket resolution time", "Average time to resolve support tickets.", "hours"), ("CSAT", "Customer satisfaction score for support.", "%"), ("First contact resolution", "Percentage resolved on first contact.", "%")],
    [("Feature adoption", "Percentage of users using new features.", "%"), ("NPS for product", "Product-specific NPS score.", "score"), ("Release cadence", "Releases per quarter.", "count")],
    [("NRR", "Net revenue retention.", "%"), ("Churn rate", "Customer churn percentage.", "%"), ("Expansion revenue", "Upsell/cross-sell revenue.", "currency")],
    [("Design delivery on time", "Percentage of design deliverables on schedule.", "%"), ("Usability score", "Post-release usability score.", "score"), ("Design system coverage", "Components in design system.", "count")],
]

# ---------------------------------------------------------------------------
# Notification templates: (title, message, type)
# ---------------------------------------------------------------------------
NOTIFICATION_TEMPLATES = [
    ("Welcome to EPMS", "Your profile and starter goals have been created. Review and adjust as needed.", "info"),
    ("New goal assigned", "A new goal has been added to your profile. Please review and confirm.", "info"),
    ("Review submitted", "Your manager has submitted your performance review. You can view it in Reviews.", "success"),
    ("1:1 scheduled", "A 1:1 meeting has been scheduled with your manager. Check Meetings for details.", "info"),
    ("Training assigned", "You have been enrolled in a training program. Check the Training section.", "info"),
    ("Feedback received", "You have received new feedback from a colleague. View it in Feedback.", "info"),
]
