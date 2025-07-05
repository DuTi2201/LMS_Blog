'use client';

import { useState } from 'react';
import Image from 'next/image';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { CheckCircle, Users, BookOpen, Target, TrendingUp, Code, Brain, Zap, ChevronDown, Award, Star } from 'lucide-react';
import { Header } from '@/components/header';

const skillCategories = [
  {
    title: "1. Lập trình Python cơ bản và nâng cao",
    description: "Thành thạo cú pháp Python, cấu trúc dữ liệu (Data Structures), và lập trình hướng đối tượng (OOP). Ứng dụng Python vào các bài toán thực tế trong AI/ML.",
    skills: ["Python", "DataStructures", "OOP"],
    icon: <Code className="w-6 h-6" />,
    color: "bg-blue-500"
  },
  {
    title: "2. Nền tảng Toán và Machine Learning cơ bản",
    description: "Hiểu các khái niệm toán học cốt lõi (đại số, xác suất) hỗ trợ AI. Xây dựng mô hình Machine Learning cơ bản (hồi quy, phân loại).",
    skills: ["Math", "Machine Learning"],
    icon: <Brain className="w-6 h-6" />,
    color: "bg-green-500"
  },
  {
    title: "3. Deep Learning toàn diện",
    description: "Nắm vững kiến trúc Neural Network, CNN (ảnh), RNN/Transformer (văn bản). Thực hành với frameworks như TensorFlow/PyTorch.",
    skills: ["Deep Learning", "CNN", "RNN", "Transformer", "PyTorch"],
    icon: <Zap className="w-6 h-6" />,
    color: "bg-purple-500"
  },
  {
    title: "4. Ứng dụng AI trong thực tế",
    description: "Xử lý dữ liệu đa dạng: bảng biểu, chuỗi thời gian, hình ảnh, văn bản. Phát triển Generative Models (GAN, Diffusion) và Large Language Models (LLM).",
    skills: ["Generative", "GAN", "Diffusion", "LLM"],
    icon: <Target className="w-6 h-6" />,
    color: "bg-orange-500"
  },
  {
    title: "5. Kỹ năng chuyên sâu",
    description: "Tối ưu mô hình, triển khai sản phẩm AI. Đọc hiểu tài liệu nghiên cứu và cập nhật xu hướng AI mới.",
    skills: ["Optimize models", "Research skill"],
    icon: <TrendingUp className="w-6 h-6" />,
    color: "bg-red-500"
  }
];

const targetAudience = [
  {
    title: "Người mới bắt đầu - bắt đầu từ số 0",
    description: "Bạn chưa từng học lập trình? Bạn thấy Toán là khó khăn? Không sao cả! AIO xây dựng lộ trình từ nền tảng vững chắc.",
    icon: <Users className="w-8 h-8" />,
    features: [
      "Từ Python căn bản, Toán ứng dụng, đến các kỹ năng AI chuyên sâu.",
      "Có mentor và cộng đồng đồng hành suốt 1 năm."
    ]
  },
  {
    title: "Người đi làm - muốn nâng cấp bản thân hoặc chuyển hướng sự nghiệp",
    description: "Đã có ít kỹ sự phần mềm, chuyển viên tài chính, nhà phân tích dữ liệu hay marketer,... AIO giúp bạn học đúng - học đủ - học sâu để tối ưu công việc hiện tại hoặc chuyển mình sang Data/AI một cách bài bản.",
    icon: <BookOpen className="w-8 h-8" />,
    features: [
      "Áp dụ tối ưu công việc hiện tại hoặc chuyển mình sang Data/AI một cách bài bản."
    ]
  },
  {
    title: "Sinh viên các ngành - chuẩn bị cho tương lai dữ liệu",
    description: "Bạn đang học CNTT, Toán ứng dụng, Khoa học dữ liệu, Kinh tế... và muốn có thêm kỹ năng AI? AIO là lựa chọn hoàn hảo cho bạn.",
    icon: <Target className="w-8 h-8" />,
    features: [
      "Có portfolio dự án AI thực tế",
      "Có định hướng nghề nghiệp rõ ràng",
      "Tự tin bước vào thị trường lao động với lợi thế cạnh tranh cao",
      "Suốt cùng lớp AIO2025."
    ]
  }
];

const courseModules = [
  {
    id: 1,
    title: "(Module 1) Toán cơ bản và lập trình Python",
    description: "Nền tảng toán học và lập trình Python cơ bản",
    lessons: 14,
    duration: "4 tuần",
    isExpanded: false,
    content: [
      "01. Lập trình python cơ bản",
      "02. Data Structure (list~IoU, Top-K Searching)",
      "03. Data Structure (Graph and Tree)",
      "04. Lập trình hướng đối tượng (Python)",
      "05. Lập trình hướng đối tượng (Pytorch)",
      "06. TA-Exercise",
      "07. Lớp nâng cao: SQL (3 buổi)",
      "08. Lớp nâng cao: Phương pháp coding hiệu quả",
      "09. Lớp nâng cao: Git&Github for Version Control",
      "10. Lớp nâng cao: Unix&Docker",
      "11. Bài thi cuối Module",
      "12. Project 1.1: Xây dựng hệ thống camera an ninh ban đêm",
      "13. Project 1.2: Tạo và triển khai một chatbot cho một chủ đề cá nhân",
      "14. Basic Web and Streamlit (for projects 1.1 and 1.2)"
    ]
  },
  {
    id: 2,
    title: "(Module 2) Lập trình nâng cao và ứng dụng trong AI",
    description: "Kỹ thuật lập trình nâng cao cho AI",
    lessons: 13,
    duration: "3 tuần",
    isExpanded: false,
    content: [
      "01. Lập trình Numpy; Vector and Matrix",
      "02. Đo mức độ tương đồng của dữ liệu dùng Cosine similarity",
      "03. Xác suất thống kê cơ bản và ứng dụng vào AI",
      "04. Ứng dụng Correlation Coefficient vào các bài toán thực tế",
      "05. Phân loại dữ liệu dùng Naïve Bayes classifier",
      "06. TA-Exercise",
      "07. Lớp nâng cao: NoSQL database",
      "08. Lớp nâng cao: Logic Thinking for AI",
      "09. Lớp nâng cao: Effective Data Presentation Skills",
      "10. Bài thi cuối Module",
      "11. Project 2.1: Đánh giá cảm xúc khách hàng từ các comment phản hồi",
      "12. Project 2.2: Xây dựng hệ thống tìm kiếm ảnh",
      "13. Vector database (for projects 2.1 and 2.2)"
    ]
  },
  {
    id: 3,
    title: "(Module 3) Máy học cơ bản",
    description: "Các thuật toán machine learning cơ bản",
    lessons: 13,
    duration: "3 tuần",
    isExpanded: false,
    content: [
      "01. Data Visualization and Analysis",
      "02. K-Mean",
      "03. KNN: K-Nearest Neighbors",
      "04. Bài toán phân loại dùng Decision Tree",
      "05. TA-Exercise",
      "06. Lớp nâng cao: Databricks for Big Data Processing (+Spark)",
      "07. Lớp nâng cao: Excel+Tableau and Databricks for Data Analysis",
      "08. Lớp nâng cao: PySpark for Data Processing",
      "09. Lớp nâng cao: ETL Pipelines",
      "10. Lớp nâng cao: Cloud for Data Storage and Management",
      "11. Bài thi cuối Module",
      "12. Text Project 3.1: Phân loại chủ đề của một bài báo",
      "13. Tabular Data Project 3.2: Phân loại khả năng mắc bệnh tim"
    ]
  },
  {
    id: 4,
    title: "(Module 4) Máy học (table and time series)",
    description: "Machine learning cho dữ liệu bảng và chuỗi thời gian",
    lessons: 13,
    duration: "4 tuần",
    isExpanded: false,
    content: [
      "01. Random Forest",
      "02. AdaBoost, Gradient Boost",
      "03. XGBoost, CatBoost",
      "04. LightGBM",
      "05. TA-Exercise",
      "06. MLOps: Streamlit and Gradio",
      "07. MLOps: Fastapi",
      "08. MLOps: Dockerize Gradio and Fastapi",
      "09. Lớp nâng cao: XAI",
      "10. Bài thi cuối Module",
      "11. Time-series Project 4.1: Dự đoán mức độ ô nhiễm từ các thông tin đặc trưng",
      "12. Tabular Data Project 4.2: Dự đoán giá thuê phòng dùng dữ liệu Airbnb",
      "13. Project thực tế: Sales Forecasting and Demand Prediction"
    ]
  },
  {
    id: 5,
    title: "(Module 5) Step into Deep Learning 1",
    description: "Bước đầu vào Deep Learning",
    lessons: 13,
    duration: "4 tuần",
    isExpanded: false,
    content: [
      "01. Linear Regression (L1, L2, and Huber losses)",
      "02. Vectorization for Linear Regression",
      "03. Randomness and Genetic Algorithms",
      "04. Genetic Algorithms (Optimization and Linear regression)",
      "05. TA-Exercise",
      "06. MLOps: Speed up Model Inferencing Using Numba+TorchScript",
      "07. MLOps: Model Serving and Packaging",
      "08. MLOps: Triton Inference Server",
      "09. Lớp nâng cao: Non-linear Regression",
      "10. Lớp nâng cao: Survey on Evolutionary Algorithms",
      "11. Bài thi cuối Module",
      "12. Project: Đánh giá các thuận toán trên bài toán xâm nhập mặn",
      "13. Project thực tế: Xây dựng công cụ tối ưu hoá quy trình phân bổ"
    ]
  },
  {
    id: 6,
    title: "(Module 6) Step into Deep Learning 2",
    description: "Deep Learning nâng cao",
    lessons: 13,
    duration: "4 tuần",
    isExpanded: false,
    content: [
      "01. From Linear Regressiong to Logistic Regression (Binary Classification)",
      "02. Logistic Regression - Vectorization and Application",
      "03. Softmax Regression (Multi-class Classification)",
      "04. Multilayer Perceptron",
      "05. TA-Exercise",
      "06. MLOps: AirFlow for Scheduling",
      "07. MLOps: MLFlow for Model Tracking and Versioning",
      "08. MLOps: Tracking and Logging Applications",
      "09. Lớp nâng cao: Multi-labels Classification",
      "10. Lớp nâng cao: Loss and Metric Functions for Classification",
      "11. Time-series Data Project: Dự đoán chính xác với mô hình DLinear và NLinear",
      "12. IoT Project: Điều khiển thiết bị điện tử qua tương tác cử chỉ",
      "13. Project thực tế: Customer Analysis/Churn Prediction"
    ]
  },
  {
    id: 7,
    title: "(Module 7) Insight into Deep Learning",
    description: "Hiểu sâu về Deep Learning",
    lessons: 13,
    duration: "4 tuần",
    isExpanded: false,
    content: [
      "01. Activations",
      "02. Initializers",
      "03. Optimizers for Neural Networks",
      "04. MLP Variant: Mixer",
      "05. TA-Exercise",
      "06. MLOps: CICD Pipeline",
      "07. MLOps: Model Quantization",
      "08. MLOps: Model Pruning",
      "09. Lớp nâng cao: Recent Advances in Activations, Initializers, Optmizers",
      "10. Bài thi cuối Module",
      "11. Project 7.1: Giải vấn đề Gradient Vanishing trong MLP bằng nhiều cách khác nhau",
      "12. Project 7.2: So sánh MLP và Mixer cho các dữ liệu khác nhau",
      "13. MLOps for projects 7.1 and 7.2"
    ]
  },
  {
    id: 8,
    title: "(Module 8) Different Deep Architectures for Different Data",
    description: "Kiến trúc Deep Learning cho các loại dữ liệu khác nhau",
    lessons: 13,
    duration: "4 tuần",
    isExpanded: false,
    content: [
      "01. Basic CNN (Image), Training and Generalization",
      "02. RNN, LSTM/GRU (Time-series and Text)",
      "03. Transformer (Encoder - Text Classification)",
      "04. Transformer for Image and Time-series Data",
      "05. TA-Exercise",
      "06. MLOps: Advanced inference tools (Triton and BentoML)",
      "07. MLOps: On-premise server vs Serverless - Fast production",
      "08. Lớp nâng cao: Advanced CNN Architecture",
      "09. Lớp nâng cao: Unsupervised Learning và Distillation",
      "10. Bài thi cuối Module",
      "11. Image Project 8.1: OCR (Yolov10+CNN) Information Extraction from ID Card",
      "12. Image-Text Project 8.2: Vision QA",
      "13. MLOps for Projects 8.1 and 8.2"
    ]
  },
  {
    id: 9,
    title: "(Module 9) Deep Learning Applications for Images",
    description: "Ứng dụng Deep Learning cho xử lý ảnh",
    lessons: 14,
    duration: "4 tuần",
    isExpanded: false,
    content: [
      "01. Domain Conversion - Denoising and Segmentation",
      "02. Domain Conversion - Colorization and Super-resolution",
      "03. Object Detection",
      "04. TA-Exercise",
      "05. Lớp nâng cao: VideoCLIP for Video Classification",
      "06. Lớp nâng cao: Stereo Depth Estimation",
      "07. Lớp nâng cao: Monodepth Estimation",
      "08. Lớp nâng cao: Mamba",
      "09. Research: Mamba - Research Directions",
      "10. Bài thi cuối Module",
      "11. MLOps: Kafka",
      "12. Image Project 9.1: Footballer Tracking",
      "13. Research Project 9.2: Advances in Medical Image Analysis",
      "14. MLOps for Projects 9.1 and 9.2"
    ]
  },
  {
    id: 10,
    title: "(Module 10) Deep Learning Applications for Text",
    description: "Ứng dụng Deep Learning cho xử lý văn bản",
    lessons: 14,
    duration: "4 tuần",
    isExpanded: false,
    content: [
      "01. From Text Classification to POS Tagging",
      "02. NER for Medical Data",
      "03. Text Summarization and Generation",
      "04. Machine Translation",
      "05. TA-Exercise",
      "06. Lớp nâng cao: Question Answering",
      "07. Lớp nâng cao: Document Retrieval",
      "08. Lớp nâng cao: Speech Recognition",
      "09. Lớp nâng cao: Advances in Tokenization",
      "10. Lớp nâng cao: Augmented SBERT",
      "11. MLOps: Docker Swarm",
      "12. Project 10.1: Xây dựng hệ thống sinh lời thoại cho truyện tranh",
      "13. Project 10.2: Xây dựng hệ thống dịch đa ngôn ngữ",
      "14. MLOps for Projects 10.1 and 10.2"
    ]
  },
  {
    id: 11,
    title: "(Module 11) Generative Models",
    description: "Mô hình sinh dữ liệu",
    lessons: 14,
    duration: "4 tuần",
    isExpanded: false,
    content: [
      "01. Basic Style Transfer",
      "02. Multi-modal Style Transfer",
      "03. GAN and CDGAN",
      "04. Pix2Pix and Cycle GAN",
      "05. Diffusion Models",
      "06. TA-Exercise",
      "07. Lớp nâng cao: GNN (Node Classification)",
      "08. Lớp nâng cao: GNN (Molecular Property Prediction)",
      "09. Lớp nâng cao: Advances in GNN",
      "10. Lớp nâng cao: Flow Matching",
      "11. MLOps: Kubernetes",
      "12. Project 11.1: Diffusion-based Image Colorization",
      "13. Project 11.2: Image Generation",
      "14. MLOps for project 11.1 and 11.2"
    ]
  },
  {
    id: 12,
    title: "(Module 12) Large Language Models",
    description: "Mô hình ngôn ngữ lớn",
    lessons: 13,
    duration: "4 tuần",
    isExpanded: false,
    content: [
      "01. Pretraining LLM (GPT)",
      "02. RAG, Prompting and Langchain",
      "03. Parameter-Efficient Fine-Tuning (LoRA, QLoRA)",
      "04. Instruction tuning (prompt for training)",
      "05. LLM Reasoning: Chain-of-Thought and DeepSeek Model",
      "06. Enhancing LLMs with Reinforcement Learning (RLHF, DPO))",
      "07. AI Agents with LLMs: Using Libraries, Tool Calling",
      "08. AI Agents with LLMs: ReAct Agents",
      "09. Vision Language Model",
      "10. Project 12.1 PEFT for multiple-choice QA",
      "11. Project 12.2 Chatbot using LLMs",
      "12. Project 12.3 Agentic AI using Vision Language Model",
      "13. LLMOps for project 12.1"
    ]
  }
];

export default function AboutPage() {
  const [activeTab, setActiveTab] = useState('overview');
  const [modules, setModules] = useState(courseModules);

  const toggleModule = (id: number) => {
    setModules(modules.map(module => 
      module.id === id ? { ...module, isExpanded: !module.isExpanded } : module
    ));
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      <Header />
      {/* Hero Section */}
      <section className="relative py-20 px-4 text-center">
        <div className="max-w-6xl mx-auto">
          <h1 className="text-4xl md:text-6xl font-bold text-gray-900 mb-6">
            Khóa All - In - One (AIO)
            <span className="block text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600">
              Khoa Học Dữ Liệu Và Trí Tuệ Nhân Tạo
            </span>
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
            Dành cho những ai đam mê khoa học dữ liệu và trí tuệ nhân tạo – phù hợp cả 
            với người mới bắt đầu, không có nền tảng lập trình hoặc muốn chuyển ngành.
          </p>
           {/* Course Roadmap Image */}
      <section className="py-16 px-4">
        <div className="max-w-6xl mx-auto">
          <div className="bg-white rounded-2xl shadow-xl p-8">
            <Image
              src="/AIO_2025_v3_4c92b0d78d.svg"
              alt="AIO 2025 Course Roadmap"
              width={1200}
              height={600}
              className="w-full h-auto rounded-lg"
              priority
            />
          </div>
        </div>
      </section>
        </div>
      </section>

    

      {/* Target Audience Section */}
      <section className="py-16 px-4 bg-white">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl md:text-4xl font-bold text-center text-gray-900 mb-12">
            Khóa học này dành cho ai?
          </h2>
          <div className="grid md:grid-cols-3 gap-8">
            {targetAudience.map((audience, index) => (
              <Card key={index} className="h-full hover:shadow-lg transition-shadow">
                <CardHeader className="text-center">
                  <div className="mx-auto mb-4 p-3 bg-blue-100 rounded-full w-fit">
                    {audience.icon}
                  </div>
                  <CardTitle className="text-lg font-semibold text-gray-900">
                    {audience.title}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-gray-600 mb-4">
                    {audience.description}
                  </CardDescription>
                  <ul className="space-y-2">
                    {audience.features.map((feature, featureIndex) => (
                      <li key={featureIndex} className="flex items-start gap-2">
                        <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                        <span className="text-sm text-gray-600">{feature}</span>
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Learning Outcomes Section */}
      <section className="py-16 px-4 bg-gray-50">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl md:text-4xl font-bold text-center text-gray-900 mb-12">
            Học viên sẽ học được gì?
          </h2>
          <div className="space-y-8">
            {skillCategories.map((category, index) => (
              <Card key={index} className="overflow-hidden hover:shadow-lg transition-shadow">
                <CardHeader className="bg-gradient-to-r from-gray-50 to-blue-50">
                  <div className="flex items-center gap-4">
                    <div className={`p-3 rounded-full ${category.color} text-white`}>
                      {category.icon}
                    </div>
                    <div className="flex-1">
                      <CardTitle className="text-xl font-semibold text-gray-900">
                        {category.title}
                      </CardTitle>
                      <CardDescription className="text-gray-600 mt-2">
                        {category.description}
                      </CardDescription>
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="pt-6">
                  <div className="flex flex-wrap gap-2">
                    {category.skills.map((skill, skillIndex) => (
                      <Badge 
                        key={skillIndex} 
                        variant="secondary" 
                        className="bg-blue-100 text-blue-800 hover:bg-blue-200 px-3 py-1"
                      >
                        {skill}
                      </Badge>
                    ))}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Course Content Section */}
      <section className="py-16 px-4 bg-white">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-3xl md:text-4xl font-bold text-center text-gray-900 mb-12">
            Nội dung khóa học
          </h2>
          <div className="space-y-4">
            {modules.map((module) => (
              <Card key={module.id} className="overflow-hidden hover:shadow-md transition-shadow">
                <CardHeader 
                  className="cursor-pointer bg-gray-50 hover:bg-gray-100 transition-colors"
                  onClick={() => toggleModule(module.id)}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <div className="w-10 h-10 bg-green-600 text-white rounded-full flex items-center justify-center font-semibold">
                        {module.id}
                      </div>
                      <CardTitle className="text-lg font-medium text-gray-900">
                        {module.title}
                      </CardTitle>
                    </div>
                    <ChevronDown 
                      className={`w-5 h-5 text-gray-500 transition-transform ${
                        module.isExpanded ? 'rotate-180' : ''
                      }`} 
                    />
                  </div>
                </CardHeader>
                {module.isExpanded && (
                  <CardContent className="pt-6">
                    <div className="space-y-4">
                      <div className="flex items-center gap-4 text-sm text-gray-600">
                        <span className="flex items-center gap-1">
                          <BookOpen className="w-4 h-4" />
                          {module.lessons} bài học
                        </span>
                        <span className="flex items-center gap-1">
                          <Target className="w-4 h-4" />
                          {module.duration}
                        </span>
                      </div>
                      <p className="text-gray-600 mb-4">
                        {module.description}
                      </p>
                      <div className="space-y-2">
                        <h4 className="font-semibold text-gray-900">Nội dung chi tiết:</h4>
                        <ul className="space-y-1">
                          {module.content?.map((item, index) => (
                            <li key={index} className="flex items-start gap-2">
                              <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                              <span className="text-sm text-gray-600">{item}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  </CardContent>
                )}
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Blog Features Section */}
      <section className="py-16 bg-gradient-to-r from-blue-50 to-indigo-50">
        <div className="max-w-4xl mx-auto px-6">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              Tính năng Blog & Chia sẻ Kiến thức
            </h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Nền tảng blog tích hợp giúp học viên và giảng viên chia sẻ kiến thức, 
              kinh nghiệm và cập nhật xu hướng công nghệ mới nhất trong lĩnh vực AI.
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-8">
            <Card className="border-0 shadow-lg hover:shadow-xl transition-shadow duration-300">
              <CardHeader>
                <div className="flex items-center gap-3 mb-2">
                  <div className="p-2 bg-blue-100 rounded-lg">
                    <BookOpen className="w-6 h-6 text-blue-600" />
                  </div>
                  <CardTitle className="text-xl">Quản lý Nội dung</CardTitle>
                </div>
                <CardDescription>
                  Hệ thống quản lý blog chuyên nghiệp với editor WYSIWYG
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="space-y-3">
                  <li className="flex items-start gap-2">
                    <CheckCircle className="w-5 h-5 text-green-500 mt-0.5 flex-shrink-0" />
                    <span className="text-gray-600">Editor markdown với preview real-time</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle className="w-5 h-5 text-green-500 mt-0.5 flex-shrink-0" />
                    <span className="text-gray-600">Upload và quản lý hình ảnh, file đính kèm</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle className="w-5 h-5 text-green-500 mt-0.5 flex-shrink-0" />
                    <span className="text-gray-600">Phân loại bài viết theo chủ đề và tags</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle className="w-5 h-5 text-green-500 mt-0.5 flex-shrink-0" />
                    <span className="text-gray-600">Lên lịch xuất bản tự động</span>
                  </li>
                </ul>
              </CardContent>
            </Card>

            <Card className="border-0 shadow-lg hover:shadow-xl transition-shadow duration-300">
              <CardHeader>
                <div className="flex items-center gap-3 mb-2">
                  <div className="p-2 bg-green-100 rounded-lg">
                    <Users className="w-6 h-6 text-green-600" />
                  </div>
                  <CardTitle className="text-xl">Cộng đồng Học tập</CardTitle>
                </div>
                <CardDescription>
                  Kết nối và chia sẻ kiến thức trong cộng đồng AI
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="space-y-3">
                  <li className="flex items-start gap-2">
                    <CheckCircle className="w-5 h-5 text-green-500 mt-0.5 flex-shrink-0" />
                    <span className="text-gray-600">Bình luận và thảo luận trên bài viết</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle className="w-5 h-5 text-green-500 mt-0.5 flex-shrink-0" />
                    <span className="text-gray-600">Đánh giá và like bài viết</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle className="w-5 h-5 text-green-500 mt-0.5 flex-shrink-0" />
                    <span className="text-gray-600">Theo dõi tác giả yêu thích</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle className="w-5 h-5 text-green-500 mt-0.5 flex-shrink-0" />
                    <span className="text-gray-600">Chia sẻ bài viết trên mạng xã hội</span>
                  </li>
                </ul>
              </CardContent>
            </Card>

            <Card className="border-0 shadow-lg hover:shadow-xl transition-shadow duration-300">
              <CardHeader>
                <div className="flex items-center gap-3 mb-2">
                  <div className="p-2 bg-purple-100 rounded-lg">
                    <Target className="w-6 h-6 text-purple-600" />
                  </div>
                  <CardTitle className="text-xl">Tìm kiếm Thông minh</CardTitle>
                </div>
                <CardDescription>
                  Công cụ tìm kiếm và lọc nội dung hiệu quả
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="space-y-3">
                  <li className="flex items-start gap-2">
                    <CheckCircle className="w-5 h-5 text-green-500 mt-0.5 flex-shrink-0" />
                    <span className="text-gray-600">Tìm kiếm full-text trong nội dung</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle className="w-5 h-5 text-green-500 mt-0.5 flex-shrink-0" />
                    <span className="text-gray-600">Lọc theo danh mục và tags</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle className="w-5 h-5 text-green-500 mt-0.5 flex-shrink-0" />
                    <span className="text-gray-600">Sắp xếp theo độ phổ biến, ngày đăng</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle className="w-5 h-5 text-green-500 mt-0.5 flex-shrink-0" />
                    <span className="text-gray-600">Gợi ý bài viết liên quan</span>
                  </li>
                </ul>
              </CardContent>
            </Card>

            <Card className="border-0 shadow-lg hover:shadow-xl transition-shadow duration-300">
              <CardHeader>
                <div className="flex items-center gap-3 mb-2">
                  <div className="p-2 bg-orange-100 rounded-lg">
                    <TrendingUp className="w-6 h-6 text-orange-600" />
                  </div>
                  <CardTitle className="text-xl">Phân tích & Thống kê</CardTitle>
                </div>
                <CardDescription>
                  Theo dõi hiệu suất và tương tác của nội dung
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="space-y-3">
                  <li className="flex items-start gap-2">
                    <CheckCircle className="w-5 h-5 text-green-500 mt-0.5 flex-shrink-0" />
                    <span className="text-gray-600">Thống kê lượt xem và tương tác</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle className="w-5 h-5 text-green-500 mt-0.5 flex-shrink-0" />
                    <span className="text-gray-600">Báo cáo hiệu suất bài viết</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle className="w-5 h-5 text-green-500 mt-0.5 flex-shrink-0" />
                    <span className="text-gray-600">Phân tích xu hướng chủ đề</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle className="w-5 h-5 text-green-500 mt-0.5 flex-shrink-0" />
                    <span className="text-gray-600">Dashboard quản lý tổng quan</span>
                  </li>
                </ul>
              </CardContent>
            </Card>
          </div>

          <div className="text-center mt-12">
            <div className="bg-white rounded-2xl p-8 shadow-lg border border-gray-100">
              <h3 className="text-2xl font-bold text-gray-900 mb-4">
                Khám phá Blog ngay hôm nay!
              </h3>
              <p className="text-gray-600 mb-6 max-w-2xl mx-auto">
                Tham gia cộng đồng học tập, chia sẻ kiến thức và cập nhật những xu hướng 
                mới nhất trong lĩnh vực Artificial Intelligence.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <a href="/" >
                  <Button size="lg" className="bg-blue-600 hover:bg-blue-700">
                  <BookOpen className="w-5 h-5 mr-2" />
                  Đọc Blog
                </Button>
                </a>
               
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}