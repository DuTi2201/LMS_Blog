"use client"

import { useState, useEffect } from "react"
import { Header } from "@/components/header"
import { Sidebar } from "@/components/sidebar"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { ArrowRight, BookOpen, Users, TrendingUp, Calendar, Clock } from "lucide-react"
import { apiClient, BlogPost, Course } from "@/lib/api"

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
  const [recentPosts, setRecentPosts] = useState<BlogPost[]>([])
  const [featuredCourses, setFeaturedCourses] = useState<Course[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true)
        const [postsData, coursesData] = await Promise.all([
          apiClient.getBlogPosts(0, 6), // Get latest 6 posts
          apiClient.getCourses(0, 4)    // Get latest 4 courses
        ])
        
        setRecentPosts(postsData)
        setFeaturedCourses(coursesData)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch data')
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [])

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Header />
        <div className="flex">
          <Sidebar />
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
          <Sidebar />
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
        <Sidebar />
        <main className="flex-1 p-6">
          <div className="max-w-7xl mx-auto space-y-8">
            {/* Hero Section */}
            <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg p-8 text-white">
              <h1 className="text-4xl font-bold mb-4">
                Welcome to LMS Blog
              </h1>
              <p className="text-xl mb-6 opacity-90">
                Discover the latest insights, tutorials, and updates from our learning community.
              </p>
              <div className="flex gap-4">
                <Link href="/blog">
                  <Button variant="secondary" size="lg">
                    Explore Blog
                    <ArrowRight className="ml-2 h-4 w-4" />
                  </Button>
                </Link>
                <Link href="/learning">
                  <Button variant="outline" size="lg" className="text-white border-white hover:bg-white hover:text-blue-600">
                    Start Learning
                  </Button>
                </Link>
              </div>
            </div>

            {/* Stats Section */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center">
                    <BookOpen className="h-8 w-8 text-blue-600" />
                    <div className="ml-4">
                      <p className="text-sm font-medium text-gray-600">Total Posts</p>
                      <p className="text-2xl font-bold text-gray-900">{recentPosts.length}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center">
                    <Users className="h-8 w-8 text-green-600" />
                    <div className="ml-4">
                      <p className="text-sm font-medium text-gray-600">Courses</p>
                      <p className="text-2xl font-bold text-gray-900">{featuredCourses.length}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center">
                    <TrendingUp className="h-8 w-8 text-purple-600" />
                    <div className="ml-4">
                      <p className="text-sm font-medium text-gray-600">Active Learners</p>
                      <p className="text-2xl font-bold text-gray-900">1,234</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Recent Blog Posts */}
            <div>
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold text-gray-900">Recent Blog Posts</h2>
                <Link href="/blog">
                  <Button variant="outline">
                    View All Posts
                    <ArrowRight className="ml-2 h-4 w-4" />
                  </Button>
                </Link>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {recentPosts.slice(0, 6).map((post) => (
                  <Card key={post.id} className="hover:shadow-lg transition-shadow">
                    <CardContent className="p-6">
                      <div className="flex items-center gap-2 text-sm text-gray-500 mb-3">
                        <Calendar className="h-4 w-4" />
                        <span>{formatDate(post.created_at)}</span>
                        <span>•</span>
                        <Clock className="h-4 w-4" />
                        <span>{calculateReadTime(post.content)}</span>
                      </div>
                      
                      <h3 className="text-lg font-semibold text-gray-900 mb-2 line-clamp-2">
                        {post.title}
                      </h3>
                      
                      <p className="text-gray-600 mb-4 line-clamp-3">
                        {post.excerpt || post.content.substring(0, 120)}...
                      </p>
                      
                      <div className="flex items-center justify-between">
                        <div className="flex flex-wrap gap-1">
                          {post.tags.slice(0, 2).map((tag) => (
                            <Badge key={tag.id} variant="secondary" className="text-xs">
                              {tag.name}
                            </Badge>
                          ))}
                        </div>
                        
                        <Link href={`/blog/${post.id}`}>
                          <Button variant="ghost" size="sm">
                            Read More
                            <ArrowRight className="ml-1 h-3 w-3" />
                          </Button>
                        </Link>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>

            {/* Featured Courses */}
            <div>
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold text-gray-900">Featured Courses</h2>
                <Link href="/learning">
                  <Button variant="outline">
                    View All Courses
                    <ArrowRight className="ml-2 h-4 w-4" />
                  </Button>
                </Link>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                {featuredCourses.slice(0, 4).map((course) => (
                  <Card key={course.id} className="hover:shadow-lg transition-shadow">
                    <CardContent className="p-6">
                      <div className="flex items-center justify-between mb-3">
                        <Badge variant={course.difficulty_level === 'beginner' ? 'default' : course.difficulty_level === 'intermediate' ? 'secondary' : 'destructive'}>
                          {course.difficulty_level}
                        </Badge>
                        <span className="text-sm text-gray-500">
                          {Math.floor(course.estimated_duration / 60)}h {course.estimated_duration % 60}m
                        </span>
                      </div>
                      
                      <h3 className="text-lg font-semibold text-gray-900 mb-2 line-clamp-2">
                        {course.title}
                      </h3>
                      
                      <p className="text-gray-600 mb-4 line-clamp-3">
                        {course.short_description || course.description.substring(0, 100)}...
                      </p>
                      
                      <div className="flex items-center justify-between">
                        <span className="text-lg font-bold text-blue-600">
                          {course.price > 0 ? `$${course.price}` : 'Free'}
                        </span>
                        
                        <Link href={`/learning/${course.id}`}>
                          <Button size="sm">
                            Start Course
                          </Button>
                        </Link>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  )
}
