"use client"

import React, { use } from "react"
import { Header } from "@/components/header"
import { Sidebar } from "@/components/sidebar"
import { Badge } from "@/components/ui/badge"
import { Calendar, Clock, BookOpen } from "lucide-react"
import ReactMarkdown from "react-markdown"
import remarkMath from "remark-math"
import rehypeKatex from "rehype-katex"
import "katex/dist/katex.css"

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
                <ReactMarkdown
                  remarkPlugins={[remarkMath]}
                  rehypePlugins={[rehypeKatex]}
                  components={{
                    // Custom styling for different elements
                    h1: ({ children }) => (
                      <h1 className="text-2xl font-bold mt-8 mb-4 text-gray-900">
                        {children}
                      </h1>
                    ),
                    h2: ({ children }) => (
                      <h2 className="text-xl font-semibold mt-6 mb-3 text-gray-800">
                        {children}
                      </h2>
                    ),
                    h3: ({ children }) => (
                      <h3 className="text-lg font-medium mt-4 mb-2 text-gray-700">
                        {children}
                      </h3>
                    ),
                    h4: ({ children }) => (
                      <h4 className="text-base font-medium mt-3 mb-2 text-gray-700">
                        {children}
                      </h4>
                    ),
                    p: ({ children }) => (
                      <p className="mb-4 text-gray-600 leading-relaxed">
                        {children}
                      </p>
                    ),
                    code: ({ inline, children, ...props }: React.ComponentProps<'code'> & { inline?: boolean }) => (
                      inline ? (
                        <code className="bg-gray-100 px-1 py-0.5 rounded text-sm font-mono text-red-600" {...props}>
                          {children}
                        </code>
                      ) : (
                        <code className="block bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto font-mono text-sm" {...props}>
                          {children}
                        </code>
                      )
                    ),
                    pre: ({ children }) => (
                      <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto mb-4">
                        {children}
                      </pre>
                    ),
                    blockquote: ({ children }) => (
                      <blockquote className="border-l-4 border-blue-500 pl-4 italic text-gray-600 my-4">
                        {children}
                      </blockquote>
                    ),
                    table: ({ children }) => (
                      <div className="overflow-x-auto my-4">
                        <table className="min-w-full border-collapse border border-gray-300">
                          {children}
                        </table>
                      </div>
                    ),
                    th: ({ children }) => (
                      <th className="border border-gray-300 bg-gray-50 px-4 py-2 text-left font-semibold">
                        {children}
                      </th>
                    ),
                    td: ({ children }) => (
                      <td className="border border-gray-300 px-4 py-2">
                        {children}
                      </td>
                    ),
                    img: ({ src, alt }) => (
                      <img 
                        src={src} 
                        alt={alt} 
                        className="max-w-full h-auto rounded-lg shadow-md my-4 mx-auto block"
                        loading="lazy"
                      />
                    ),
                    ul: ({ children }) => (
                      <ul className="list-disc list-inside mb-4 space-y-1">
                        {children}
                      </ul>
                    ),
                    ol: ({ children }) => (
                      <ol className="list-decimal list-inside mb-4 space-y-1">
                        {children}
                      </ol>
                    ),
                    li: ({ children }) => (
                      <li className="text-gray-600">
                        {children}
                      </li>
                    )
                  }}
                >
                  {post.content}
                </ReactMarkdown>
              </div>
            </article>
          </main>
        </div>
      </div>
    </div>
  )
}
