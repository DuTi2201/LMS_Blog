"use client"

import { use } from "react"
import { Header } from "@/components/header"
import { Sidebar } from "@/components/sidebar"
import { Badge } from "@/components/ui/badge"
import { Calendar, Clock, BookOpen } from "lucide-react"

const blogPosts = {
  "1": {
    id: "1",
    title: "AIO2025 - Week 3: Object-Oriented Programming, SQL & Data Structures",
    content: `# 🎯 Learning Objectives

Master object-oriented programming principles, advanced SQL operations, and fundamental data structures through interactive visualizations and practical examples.

## 📚 Table of Contents

### 🎯 1. Object-Oriented Programming (OOP)

#### 1.1. Classes and Objects Fundamentals

| Concept | Definition | Key Characteristics |
|---------|------------|-------------------|
| Class | Blueprint for creating objects | Defines attributes and methods |
| Object | Instance of a class | Contains actual data and can execute methods |
| Attributes | Data stored in objects | Variables that hold object state |
| Methods | Functions defined in classes | Operations that objects can perform |

#### 🎨 Interactive Class-Object Relationship Visualization

The relationship between classes and objects can be visualized as a blueprint creating multiple instances, each with their own data but sharing the same structure and behavior.

### 📊 2. Database - SQL Advanced Techniques

#### 2.1. SQL JOIN Clause
#### 2.2. Subqueries (Nested Queries)
#### 2.3. Common Table Expressions (CTEs)
#### 2.4. Temporary Tables
#### 2.5. Stored Procedures and Triggers

### 📈 3. Data Structures Fundamentals

#### 3.1. Stack
#### 3.2. Queue
#### 3.3. Tree
#### 3.4. Binary Search Tree (BST)

## 🎯 1. Object-Oriented Programming (OOP)

💡 **Core Concept**: OOP is a programming paradigm based on "objects" - entities that encapsulate data (attributes) and behavior (methods) together.

### 🖥️ 1.1. Classes and Objects Fundamentals

Understanding the fundamental concepts of object-oriented programming is crucial for building scalable and maintainable applications.`,
    date: "2025-06-23",
    category: "Learning Notes",
    tags: [
      "AIO2025",
      "Object-Oriented Programming",
      "SQL",
      "Data Structures",
      "PyTorch",
      "Python",
      "Interactive Learning",
    ],
    author: "AI Blog Pro Team",
    readTime: "99 minutes",
    wordCount: "19831 words",
  },
}

interface BlogPostPageProps {
  params: Promise<{ id: string }>
}

export default function BlogPostPage({ params }: BlogPostPageProps) {
  const { id } = use(params)
  const post = blogPosts[id as keyof typeof blogPosts]

  if (!post) {
    return <div>Post not found</div>
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <div className="container mx-auto px-4 py-8">
        <div className="flex gap-8">
          <aside className="w-80 flex-shrink-0">
            <Sidebar />
          </aside>
          <main className="flex-1 max-w-4xl">
            <article className="bg-white rounded-lg shadow-sm p-8">
              <header className="mb-8">
                <div className="flex items-center space-x-4 text-sm text-gray-500 mb-4">
                  <div className="flex items-center space-x-1">
                    <span>{post.wordCount}</span>
                  </div>
                  <div className="flex items-center space-x-1">
                    <Clock className="w-4 h-4" />
                    <span>{post.readTime}</span>
                  </div>
                </div>

                <h1 className="text-3xl font-bold text-gray-900 mb-4">📚 {post.title}</h1>

                <div className="flex items-center space-x-4 text-sm text-gray-500 mb-4">
                  <div className="flex items-center space-x-1">
                    <Calendar className="w-4 h-4" />
                    <span>{post.date}</span>
                  </div>
                  <div className="flex items-center space-x-1">
                    <BookOpen className="w-4 h-4" />
                    <span>{post.category}</span>
                  </div>
                </div>

                <div className="flex flex-wrap gap-2">
                  {post.tags.map((tag) => (
                    <Badge key={tag} variant="secondary" className="text-xs">
                      #{tag}
                    </Badge>
                  ))}
                </div>
              </header>

              <div className="prose prose-lg max-w-none">
                {post.content.split("\n").map((line, index) => {
                  if (line.startsWith("# ")) {
                    return (
                      <h1 key={index} className="text-2xl font-bold mt-8 mb-4">
                        {line.substring(2)}
                      </h1>
                    )
                  } else if (line.startsWith("## ")) {
                    return (
                      <h2 key={index} className="text-xl font-semibold mt-6 mb-3">
                        {line.substring(3)}
                      </h2>
                    )
                  } else if (line.startsWith("### ")) {
                    return (
                      <h3 key={index} className="text-lg font-medium mt-4 mb-2">
                        {line.substring(4)}
                      </h3>
                    )
                  } else if (line.startsWith("#### ")) {
                    return (
                      <h4 key={index} className="text-base font-medium mt-3 mb-2">
                        {line.substring(5)}
                      </h4>
                    )
                  } else if (line.startsWith("| ")) {
                    // Simple table rendering - in a real app, you'd use a proper markdown parser
                    return (
                      <div key={index} className="font-mono text-sm bg-gray-50 p-2 rounded">
                        {line}
                      </div>
                    )
                  } else if (line.trim() === "") {
                    return <br key={index} />
                  } else {
                    return (
                      <p key={index} className="mb-4">
                        {line}
                      </p>
                    )
                  }
                })}
              </div>
            </article>
          </main>
        </div>
      </div>
    </div>
  )
}
