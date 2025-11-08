from fpdf import FPDF
import os


class ResumePDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, '', 0, 1)
    
    def add_section(self, title):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, title, 0, 1)
        self.set_font('Arial', '', 10)
    
    def add_text(self, text):
        self.multi_cell(0, 5, text)
        self.ln(2)


def create_green_candidate():
    pdf = ResumePDF()
    pdf.add_page()
    
    pdf.set_font('Arial', 'B', 20)
    pdf.cell(0, 10, 'Sarah Chen', 0, 1)
    pdf.set_font('Arial', '', 10)
    pdf.cell(0, 5, 'Email: sarah.chen@email.com | GitHub: torvalds', 0, 1)
    pdf.cell(0, 5, 'Phone: (555) 123-4567', 0, 1)
    pdf.ln(5)
    
    pdf.add_section('PROFESSIONAL SUMMARY')
    pdf.add_text('Experienced Senior Software Engineer with 8+ years of expertise in Python, JavaScript, and cloud technologies. Proven track record of delivering scalable backend systems and mentoring junior developers.')
    
    pdf.add_section('EXPERIENCE')
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(0, 7, 'Senior Software Engineer - TechCorp Inc.', 0, 1)
    pdf.set_font('Arial', 'I', 9)
    pdf.cell(0, 5, 'January 2020 - Present', 0, 1)
    pdf.set_font('Arial', '', 10)
    pdf.add_text('- Led development of microservices architecture serving 1M+ users')
    pdf.add_text('- Implemented CI/CD pipelines reducing deployment time by 60%')
    pdf.add_text('- Mentored team of 5 junior engineers')
    
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(0, 7, 'Software Engineer - DataSystems Ltd.', 0, 1)
    pdf.set_font('Arial', 'I', 9)
    pdf.cell(0, 5, 'June 2016 - December 2019', 0, 1)
    pdf.set_font('Arial', '', 10)
    pdf.add_text('- Built RESTful APIs using Python Flask and Django')
    pdf.add_text('- Optimized database queries improving performance by 40%')
    pdf.add_text('- Collaborated with cross-functional teams on product features')
    
    pdf.add_section('EDUCATION')
    pdf.add_text('Bachelor of Science in Computer Science')
    pdf.add_text('Stanford University, 2016')
    
    pdf.add_section('SKILLS')
    pdf.add_text('Python, JavaScript, TypeScript, React, Node.js, PostgreSQL, MongoDB, Docker, Kubernetes, AWS, Git')
    
    output_path = os.path.join(os.path.dirname(__file__), 'candidate_green.pdf')
    pdf.output(output_path)
    print(f"Created: {output_path}")
    return output_path


def create_yellow_candidate():
    pdf = ResumePDF()
    pdf.add_page()
    
    pdf.set_font('Arial', 'B', 20)
    pdf.cell(0, 10, 'Mike Johnson', 0, 1)
    pdf.set_font('Arial', '', 10)
    pdf.cell(0, 5, 'Email: mike.johnson@email.com', 0, 1)
    pdf.cell(0, 5, 'Phone: (555) 234-5678', 0, 1)
    pdf.ln(5)
    
    pdf.add_section('PROFESSIONAL SUMMARY')
    pdf.add_text('Full-stack developer with experience in web application development and database management. Strong problem-solving skills and ability to work in fast-paced environments.')
    
    pdf.add_section('EXPERIENCE')
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(0, 7, 'Full-Stack Developer - WebSolutions Inc.', 0, 1)
    pdf.set_font('Arial', 'I', 9)
    pdf.cell(0, 5, 'March 2022 - Present', 0, 1)
    pdf.set_font('Arial', '', 10)
    pdf.add_text('- Developed responsive web applications using React and Node.js')
    pdf.add_text('- Integrated third-party APIs and payment systems')
    pdf.add_text('- Participated in agile development sprints')
    
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(0, 7, 'Junior Developer - StartupXYZ', 0, 1)
    pdf.set_font('Arial', 'I', 9)
    pdf.cell(0, 5, 'January 2019 - July 2020', 0, 1)
    pdf.set_font('Arial', '', 10)
    pdf.add_text('- Built features for customer-facing web platform')
    pdf.add_text('- Fixed bugs and improved code quality')
    pdf.add_text('- Worked with senior developers on complex features')
    
    pdf.add_section('EDUCATION')
    pdf.add_text('Bachelor of Science in Information Technology')
    pdf.add_text('State University, 2018')
    
    pdf.add_section('SKILLS')
    pdf.add_text('JavaScript, React, Node.js, HTML, CSS, MySQL, Git, REST APIs')
    
    output_path = os.path.join(os.path.dirname(__file__), 'candidate_yellow.pdf')
    pdf.output(output_path)
    print(f"Created: {output_path}")
    return output_path


def create_red_candidate():
    pdf = ResumePDF()
    pdf.add_page()
    
    pdf.set_font('Arial', 'B', 20)
    pdf.cell(0, 10, 'John Fraud', 0, 1)
    pdf.set_font('Arial', '', 10)
    pdf.cell(0, 5, 'Email: john.fraud@email.com | GitHub: gvanrossum', 0, 1)
    pdf.cell(0, 5, 'Phone: (555) 999-9999', 0, 1)
    pdf.ln(5)
    
    pdf.add_section('PROFESSIONAL SUMMARY')
    pdf.add_text('Expert Python developer and machine learning specialist with 10+ years of experience. Deep expertise in AI/ML algorithms, neural networks, and distributed systems. Creator of multiple open-source Python libraries.')
    
    pdf.add_section('EXPERIENCE')
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(0, 7, 'Lead AI Engineer - AI Innovations Corp.', 0, 1)
    pdf.set_font('Arial', 'I', 9)
    pdf.cell(0, 5, 'January 2018 - Present', 0, 1)
    pdf.set_font('Arial', '', 10)
    pdf.add_text('- Architected deep learning models achieving 99% accuracy')
    pdf.add_text('- Led team of 15 ML engineers')
    pdf.add_text('- Published 12 research papers in top-tier conferences')
    pdf.add_text('- Developed proprietary Python frameworks used company-wide')
    
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(0, 7, 'Senior Python Developer - TechGiant Ltd.', 0, 1)
    pdf.set_font('Arial', 'I', 9)
    pdf.cell(0, 5, 'June 2013 - December 2017', 0, 1)
    pdf.set_font('Arial', '', 10)
    pdf.add_text('- Built large-scale distributed Python systems')
    pdf.add_text('- Optimized critical algorithms for 10x performance gains')
    pdf.add_text('- Contributed to core Python language development')
    
    pdf.add_section('EDUCATION')
    pdf.add_text('Ph.D. in Computer Science (Machine Learning)')
    pdf.add_text('MIT, 2013')
    pdf.add_text('Masters in Computer Science')
    pdf.add_text('Carnegie Mellon University, 2010')
    
    pdf.add_section('SKILLS')
    pdf.add_text('Python (Expert), TensorFlow, PyTorch, Keras, scikit-learn, Pandas, NumPy, Deep Learning, Neural Networks, NLP, Computer Vision, Distributed Systems, Kubernetes, Docker, AWS, GCP')
    
    pdf.add_section('OPEN SOURCE CONTRIBUTIONS')
    pdf.add_text('- Core contributor to Python language')
    pdf.add_text('- Maintainer of 5+ popular ML libraries on GitHub')
    pdf.add_text('- 50,000+ stars across repositories')
    
    output_path = os.path.join(os.path.dirname(__file__), 'candidate_red.pdf')
    pdf.output(output_path)
    print(f"Created: {output_path}")
    return output_path


if __name__ == "__main__":
    print("Creating demo resume PDFs...")
    print()
    
    green = create_green_candidate()
    print("GREEN: Clean candidate - No fraud flags expected")
    print()
    
    yellow = create_yellow_candidate()
    print("YELLOW: Employment gap detected (July 2020 - March 2022: 20 months)")
    print()
    
    red = create_red_candidate()
    print("RED: Claims expert Python developer but GitHub (gvanrossum) shows different profile")
    print("     Inflated claims about publications and contributions")
    print()
    
    print("Demo resumes created successfully!")
    print("Upload these to test the verification system.")
