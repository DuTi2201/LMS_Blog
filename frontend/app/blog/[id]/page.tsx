"use client"

import React, { use, useState, useEffect } from "react"
import { Header } from "@/components/header"
import { Sidebar } from "@/components/sidebar"
import { Badge } from "@/components/ui/badge"
import { Calendar, Clock, BookOpen } from "lucide-react"
import ReactMarkdown from "react-markdown"
import remarkMath from "remark-math"
import rehypeKatex from "rehype-katex"
import rehypeRaw from "rehype-raw"
import "katex/dist/katex.css"
import { apiClient, BlogPost } from "@/lib/api"

// Helper functions
function formatDate(dateString: string): string {
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

function calculateReadTime(content: string): string {
  const wordsPerMinute = 200
  const wordCount = content.split(/\s+/).filter(word => word.length > 0).length
  const readTime = Math.ceil(wordCount / wordsPerMinute)
  return `${readTime} min read`
}

function calculateWordCount(content: string): string {
  const wordCount = content.split(/\s+/).filter(word => word.length > 0).length
  return `${wordCount} words`
}

interface BlogPostPageProps {
  params: Promise<{ id: string }>
}

export default function BlogPostPage({ params }: BlogPostPageProps) {
  const { id } = use(params)
  const [post, setPost] = useState<BlogPost | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchPost = async () => {
      try {
        setLoading(true)
        const blogPost = await apiClient.getBlogPost(id)
        setPost(blogPost)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch blog post')
      } finally {
        setLoading(false)
      }
    }

    fetchPost()
  }, [id])

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Header />
        <div className="container mx-auto px-4 py-8">
          <div className="flex gap-8">
            <aside className="w-80 flex-shrink-0">
              <Sidebar 
                categories={[]}
                tags={[]}
                allPosts={[]}
                selectedCategory={null}
                selectedTag={null}
                onCategoryClick={() => {}}
                onTagClick={() => {}}
                onClearFilters={() => {}}
                setSelectedCategory={() => {}}
                setSelectedTag={() => {}}
              />
            </aside>
            <main className="flex-1 max-w-4xl">
              <div className="bg-white rounded-lg shadow-sm p-8">
                <div className="animate-pulse">
                  <div className="h-8 bg-gray-200 rounded mb-4"></div>
                  <div className="h-4 bg-gray-200 rounded mb-2"></div>
                  <div className="h-4 bg-gray-200 rounded mb-2"></div>
                  <div className="h-4 bg-gray-200 rounded mb-8"></div>
                  <div className="space-y-4">
                    <div className="h-4 bg-gray-200 rounded"></div>
                    <div className="h-4 bg-gray-200 rounded"></div>
                    <div className="h-4 bg-gray-200 rounded"></div>
                  </div>
                </div>
              </div>
            </main>
          </div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Header />
        <div className="container mx-auto px-4 py-8">
          <div className="flex gap-8">
            <aside className="w-80 flex-shrink-0">
              <Sidebar 
                categories={[]}
                tags={[]}
                allPosts={[]}
                selectedCategory={null}
                selectedTag={null}
                onCategoryClick={() => {}}
                onTagClick={() => {}}
                onClearFilters={() => {}}
                setSelectedCategory={() => {}}
                setSelectedTag={() => {}}
              />
            </aside>
            <main className="flex-1 max-w-4xl">
              <div className="bg-white rounded-lg shadow-sm p-8 text-center">
                <BookOpen className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">Post not found</h3>
                <p className="text-gray-600">{error}</p>
              </div>
            </main>
          </div>
        </div>
      </div>
    )
  }

  if (!post) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Header />
        <div className="container mx-auto px-4 py-8">
          <div className="flex gap-8">
            <aside className="w-80 flex-shrink-0">
              <Sidebar 
                categories={[]}
                tags={[]}
                allPosts={[]}
                selectedCategory={null}
                selectedTag={null}
                onCategoryClick={() => {}}
                onTagClick={() => {}}
                onClearFilters={() => {}}
                setSelectedCategory={() => {}}
                setSelectedTag={() => {}}
              />
            </aside>
            <main className="flex-1 max-w-4xl">
              <div className="bg-white rounded-lg shadow-sm p-8 text-center">
                <BookOpen className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">Post not found</h3>
                <p className="text-gray-600">The blog post you're looking for doesn't exist.</p>
              </div>
            </main>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <div className="container mx-auto px-4 py-8">
        <div className="flex gap-8">
          <aside className="w-80 flex-shrink-0">
            <Sidebar 
              categories={[]}
              tags={[]}
              allPosts={[]}
              selectedCategory={null}
              selectedTag={null}
              onCategoryClick={() => {}}
              onTagClick={() => {}}
              onClearFilters={() => {}}
              setSelectedCategory={() => {}}
              setSelectedTag={() => {}}
            />
          </aside>
          <main className="flex-1 max-w-4xl">
            <article className="bg-white rounded-lg shadow-sm p-8">
              <header className="mb-8">
                <div className="flex items-center space-x-4 text-sm text-gray-500 mb-4">
                  <div className="flex items-center space-x-1">
                    <span>{calculateWordCount(post.content)}</span>
                  </div>
                  <div className="flex items-center space-x-1">
                    <Clock className="w-4 h-4" />
                    <span>{calculateReadTime(post.content)}</span>
                  </div>
                </div>

                <h1 className="text-3xl font-bold text-gray-900 mb-4">{post.title}</h1>

                <div className="flex items-center space-x-4 text-sm text-gray-500 mb-4">
                  <div className="flex items-center space-x-1">
                    <Calendar className="w-4 h-4" />
                    <span>{formatDate(post.created_at)}</span>
                  </div>
                  {post.category && (
                    <div className="flex items-center space-x-1">
                      <BookOpen className="w-4 h-4" />
                      <span>{post.category.name}</span>
                    </div>
                  )}
                  {post.author && (
                    <div className="flex items-center space-x-1">
                      <span>by {post.author.full_name}</span>
                    </div>
                  )}
                </div>

                {post.tags.length > 0 && (
                  <div className="flex flex-wrap gap-2 mb-6">
                    {post.tags.map((tag) => (
                      <Badge key={tag.id} variant="secondary" className="text-xs">
                        #{tag.name}
                      </Badge>
                    ))}
                  </div>
                )}
              </header>

              <div className="prose prose-lg max-w-none">
                <ReactMarkdown
                  remarkPlugins={[remarkMath]}
                  rehypePlugins={[rehypeKatex, rehypeRaw]}
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
