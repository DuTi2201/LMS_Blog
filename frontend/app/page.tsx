"use client"

import { useState, useEffect } from "react"
import { Header } from "@/components/header"
import { Sidebar } from "@/components/sidebar"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { ArrowRight, BookOpen, Calendar, Clock } from "lucide-react"
import { apiClient, BlogPost, Category, Tag } from "@/lib/api"
import ReactMarkdown from 'react-markdown'
import remarkMath from 'remark-math'
import rehypeKatex from 'rehype-katex'
import rehypeRaw from 'rehype-raw'
import 'katex/dist/katex.min.css'

// Helper functions
const calculateReadTime = (content: string): string => {
  const wordsPerMinute = 200
  const words = content.split(' ').length
  const minutes = Math.ceil(words / wordsPerMinute)
  return `${minutes} min read`
}

const formatDate = (dateString: string): string => {
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

export default function HomePage() {
  const [publishedPosts, setPublishedPosts] = useState<BlogPost[]>([])
  const [allPosts, setAllPosts] = useState<BlogPost[]>([])
  const [categories, setCategories] = useState<Category[]>([])
  const [tags, setTags] = useState<Tag[]>([])
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null)
  const [selectedTag, setSelectedTag] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true)
        const [postsData, categoriesData, tagsData] = await Promise.all([
          apiClient.getBlogPosts(0, 100),
          apiClient.getBlogCategories(),
          apiClient.getBlogTags()
        ])
        const published = postsData.filter(post => post.is_published)
        setAllPosts(published)
        setPublishedPosts(published)
        setCategories(categoriesData)
        setTags(tagsData)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch data')
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [])

  // Filter posts based on selected category and tag
  useEffect(() => {
    let filtered = allPosts
    
    if (selectedCategory) {
      filtered = filtered.filter(post => {
        const category = categories.find(cat => cat.id === post.category_id)
        return category?.name === selectedCategory
      })
    }
    
    if (selectedTag) {
      filtered = filtered.filter(post => 
        post.tags.some(tag => tag.name === selectedTag)
      )
    }
    
    setPublishedPosts(filtered)
  }, [selectedCategory, selectedTag, allPosts, categories])

  const handleCategoryClick = (categoryName: string) => {
    setSelectedCategory(selectedCategory === categoryName ? null : categoryName)
  }

  const handleTagClick = (tagName: string) => {
    setSelectedTag(selectedTag === tagName ? null : tagName)
  }

  const clearFilters = () => {
    setSelectedCategory(null)
    setSelectedTag(null)
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Header />
        <div className="flex">
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
          <main className="flex-1 p-6">
            <div className="max-w-7xl mx-auto">
              <div className="text-center py-12">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
                <p className="mt-4 text-gray-600">Loading...</p>
              </div>
            </div>
          </main>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Header />
        <div className="flex">
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
          <main className="flex-1 p-6">
            <div className="max-w-7xl mx-auto">
              <div className="text-center py-12">
                <p className="text-red-600">Error: {error}</p>
                <Button 
                  onClick={() => window.location.reload()} 
                  className="mt-4"
                >
                  Retry
                </Button>
              </div>
            </div>
          </main>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <div className="flex">
        <Sidebar 
          categories={categories}
          tags={tags}
          allPosts={allPosts}
          selectedCategory={selectedCategory}
          selectedTag={selectedTag}
          onCategoryClick={handleCategoryClick}
          onTagClick={handleTagClick}
          onClearFilters={clearFilters}
          setSelectedCategory={setSelectedCategory}
          setSelectedTag={setSelectedTag}
        />
        <main className="flex-1">
          <div className="max-w-7xl mx-auto px-6 py-8">
            {/* Blog Posts */}
            <div className="flex-1">
              <div className="mb-6">
                <div className="flex items-center justify-between">
                  <div>
                    <h2 className="text-2xl font-bold text-gray-900 mb-2">
                      Published Posts
                      {(selectedCategory || selectedTag) && (
                        <span className="text-lg font-normal text-gray-600 ml-2">
                          ({publishedPosts.length} filtered)
                        </span>
                      )}
                    </h2>
                    <p className="text-gray-600">Discover our latest insights and tutorials</p>
                  </div>
                </div>
              </div>
            
              <div>
              {publishedPosts.length === 0 ? (
                <div className="text-center py-12">
                  <BookOpen className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">No published posts yet</h3>
                  <p className="text-gray-600">Check back later for new content!</p>
                </div>
              ) : (
                <div className="space-y-6">
                  {publishedPosts.map((post) => {
                    const categoryName = categories.find(cat => cat.id === post.category_id)?.name || 'Uncategorized'
                    return (
                      <Card key={post.id} className="hover:shadow-lg transition-all duration-200 border-l-4 border-l-blue-500">
                        <CardContent className="p-6">
                          <div className="flex items-start justify-between">
                            <div className="flex-1">
                              <div className="flex items-center gap-3 mb-3">
                                <Calendar className="h-4 w-4 text-gray-500" />
                                <span className="text-sm text-gray-500">{formatDate(post.created_at)}</span>
                                <Badge variant="outline" className="text-xs">
                                  📚 {categoryName}
                                </Badge>
                              </div>
                              
                              <Link href={`/blog/${post.id}`}>
                                <h2 className="text-xl font-bold text-gray-900 mb-3 hover:text-blue-600 transition-colors cursor-pointer">
                                  {post.title}
                                </h2>
                              </Link>
                              
                              {post.tags.length > 0 && (
                                <div className="flex flex-wrap gap-2 mb-4">
                                  {post.tags.map((tag) => (
                                    <Badge key={tag.id} variant="secondary" className="text-xs px-2 py-1">
                                      #{tag.name}
                                    </Badge>
                                  ))}
                                </div>
                              )}
                              
                              <div className="text-gray-600 mb-4 line-clamp-3 leading-relaxed prose prose-sm max-w-none">
                                <ReactMarkdown
                                  remarkPlugins={[remarkMath]}
                                  rehypePlugins={[rehypeKatex, rehypeRaw]}
                                  components={{
                                    p: ({ children }) => (
                                      <span className="text-gray-600">
                                        {children}
                                      </span>
                                    ),
                                    strong: ({ children }) => (
                                      <strong className="font-semibold">
                                        {children}
                                      </strong>
                                    ),
                                    em: ({ children }) => (
                                      <em className="italic">
                                        {children}
                                      </em>
                                    ),
                                    code: ({ children }) => (
                                      <code className="bg-gray-100 px-1 py-0.5 rounded text-sm font-mono text-red-600">
                                        {children}
                                      </code>
                                    ),
                                    // Remove other elements for excerpt
                                    h1: () => null,
                                    h2: () => null,
                                    h3: () => null,
                                    h4: () => null,
                                    h5: () => null,
                                    h6: () => null,
                                    blockquote: () => null,
                                    ul: () => null,
                                    ol: () => null,
                                    table: () => null,
                                    img: () => null
                                  }}
                                >
                                  {(post.excerpt || post.content.substring(0, 300)) + '...'}
                                </ReactMarkdown>
                              </div>
                              
                              <div className="flex items-center justify-between">
                                <div className="flex items-center gap-4 text-sm text-gray-500">
                                  <span>{post.content.split(/\s+/).filter(word => word.length > 0).length} words</span>
                                  <span className="flex items-center gap-1">
                                    <Clock className="h-4 w-4" />
                                    <span>{calculateReadTime(post.content)}</span>
                                  </span>
                                </div>
                                
                                <Link href={`/blog/${post.id}`}>
                                  <Button variant="ghost" size="sm" className="text-blue-600 hover:text-blue-700">
                                    Read More
                                    <ArrowRight className="ml-1 h-4 w-4" />
                                  </Button>
                                </Link>
                              </div>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    )
                  })}
                </div>
              )}
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  )
}
