"use client"

import { useState, useEffect } from "react"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { Calendar, Clock, Search, Filter, BookOpen, ChevronRight } from "lucide-react"
import Link from "next/link"
import { apiClient, BlogPost } from "@/lib/api"

const gradients = [
  "from-blue-400 to-purple-600",
  "from-green-400 to-blue-500",
  "from-purple-400 to-pink-500",
  "from-orange-400 to-red-500",
  "from-red-400 to-pink-500",
  "from-yellow-400 to-orange-500",
]

export function BlogList() {
  const [searchTerm, setSearchTerm] = useState("")
  const [selectedCategory, setSelectedCategory] = useState("All")
  const [posts, setPosts] = useState<BlogPost[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [categories, setCategories] = useState<string[]>(["All"])

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true)
        const [postsData, categoriesData] = await Promise.all([
          apiClient.getBlogPosts(0, 50),
          apiClient.getBlogCategories()
        ])
        
        setPosts(postsData)
        
        // Extract unique categories
        const uniqueCategories = ["All", ...categoriesData.map(cat => cat.name)]
        setCategories(uniqueCategories)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch blog posts')
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [])

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    })
  }

  const calculateReadTime = (content: string) => {
    const wordsPerMinute = 200
    const wordCount = content.split(' ').length
    const readTime = Math.ceil(wordCount / wordsPerMinute)
    return `${readTime} min read`
  }

  if (loading) {
    return (
      <div className="space-y-6">
        {[...Array(3)].map((_, i) => (
          <Card key={i} className="overflow-hidden">
            <CardContent className="p-6">
              <div className="animate-pulse">
                <div className="h-4 bg-gray-200 rounded w-1/4 mb-2"></div>
                <div className="h-6 bg-gray-200 rounded w-3/4 mb-3"></div>
                <div className="h-4 bg-gray-200 rounded w-full mb-2"></div>
                <div className="h-4 bg-gray-200 rounded w-2/3"></div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    )
  }

  if (error) {
    return (
      <div className="text-center py-8">
        <p className="text-red-600 mb-4">Error loading blog posts: {error}</p>
        <button 
          onClick={() => window.location.reload()} 
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          Retry
        </button>
      </div>
    )
  }

  // Filter posts based on search term and category
  const filteredPosts = posts.filter(post => {
    const matchesSearch = post.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         post.content.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         (post.excerpt && post.excerpt.toLowerCase().includes(searchTerm.toLowerCase()))
    const matchesCategory = selectedCategory === "All" || 
                           (post.category && post.category.name === selectedCategory)
    return matchesSearch && matchesCategory
  })

  if (filteredPosts.length === 0) {
    return (
      <div className="text-center py-8">
        <p className="text-gray-600">No blog posts found.</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Search and Filter Controls */}
      <div className="flex flex-col sm:flex-row gap-4 mb-6">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
          <Input
            placeholder="Search posts..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
        </div>
        <div className="flex items-center gap-2">
          <Filter className="h-4 w-4 text-gray-400" />
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {categories.map(category => (
              <option key={category} value={category}>
                {category}
              </option>
            ))}
          </select>
        </div>
      </div>

      {filteredPosts.map((post, index) => (
        <Card key={post.id} className="overflow-hidden hover:shadow-lg transition-shadow">
          <CardContent className="p-0">
            <div className="flex">
              <div className={`w-2 bg-gradient-to-b ${gradients[index % gradients.length]}`} />
              <div className="flex-1 p-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-4 text-sm text-gray-500 mb-3">
                      <div className="flex items-center gap-1">
                        <Calendar className="h-4 w-4" />
                        <span>{formatDate(post.created_at)}</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <Clock className="h-4 w-4" />
                        <span>{calculateReadTime(post.content)}</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <BookOpen className="h-4 w-4" />
                        <span>{post.category?.name || 'Uncategorized'}</span>
                      </div>
                    </div>

                    <Link href={`/blog/${post.id}`}>
                      <h2 className="text-xl font-semibold text-gray-900 mb-3 hover:text-blue-600 transition-colors">
                        📚 {post.title}
                      </h2>
                    </Link>

                    <div className="flex flex-wrap gap-2 mb-3">
                      {post.tags.map((tag) => (
                        <Badge key={tag.id} variant="secondary" className="text-xs">
                          #{tag.name}
                        </Badge>
                      ))}
                    </div>

                    <p className="text-gray-600 mb-4">{post.excerpt || post.content.substring(0, 150)}...</p>

                    <div className="flex items-center space-x-4 text-sm text-gray-500">
                      <span>By {post.author?.full_name || 'Anonymous'}</span>
                      {post.is_published ? (
                        <Badge variant="default" className="text-xs">Published</Badge>
                      ) : (
                        <Badge variant="secondary" className="text-xs">Draft</Badge>
                      )}
                    </div>
                  </div>

                  <Link href={`/blog/${post.id}`}>
                    <ChevronRight className="w-5 h-5 text-gray-400 hover:text-gray-600 transition-colors" />
                  </Link>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}
