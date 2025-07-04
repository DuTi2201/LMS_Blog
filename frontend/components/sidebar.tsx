"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { apiClient, Category, Tag } from "@/lib/api"

export function Sidebar() {
  const [categories, setCategories] = useState<Category[]>([])
  const [tags, setTags] = useState<Tag[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [categoriesResponse, tagsResponse] = await Promise.all([
          apiClient.getBlogCategories(),
          apiClient.getBlogTags()
        ])
        setCategories(categoriesResponse)
        setTags(tagsResponse)
      } catch (error) {
        console.error('Error fetching sidebar data:', error)
        // Set empty arrays as fallback
        setCategories([])
        setTags([])
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [])

  return (
    <div className="space-y-6">
      
       
           {/* Hero Section */}
           <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white py-12">
            <div className="max-w-4xl mx-auto px-6 text-center">
              <h1 className="text-4xl font-bold mb-4">
                AI Blog Pro Team
              </h1>
              <p className="text-lg opacity-90">
                AI Journey of AIO 2025 - Khám phá hành trình trí tuệ nhân tạo
              </p>
            </div>
          </div>
        
    

      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Categories</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="space-y-2">
              {[...Array(3)].map((_, i) => (
                <div key={i} className="flex justify-between items-center">
                  <div className="h-4 bg-gray-200 rounded w-2/3 animate-pulse"></div>
                  <div className="h-5 bg-gray-200 rounded w-8 animate-pulse"></div>
                </div>
              ))}
            </div>
          ) : categories.length > 0 ? (
            <div className="space-y-2">
              {categories.map((category) => (
                <div key={category.id} className="flex justify-between items-center">
                  <span className="text-gray-700">{category.name}</span>
                  <Badge variant="secondary">•</Badge>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500 text-sm">No categories found</p>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Tags</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="flex flex-wrap gap-2">
              {[...Array(6)].map((_, i) => (
                <div key={i} className="h-6 bg-gray-200 rounded w-16 animate-pulse"></div>
              ))}
            </div>
          ) : tags.length > 0 ? (
            <div className="flex flex-wrap gap-2">
              {tags.slice(0, 10).map((tag) => (
                <Badge key={tag.id} variant="outline" className="text-xs">
                  {tag.name}
                </Badge>
              ))}
              {tags.length > 10 && (
                <Button variant="ghost" size="sm" className="text-blue-500 p-0 h-auto">
                  +{tags.length - 10} more
                </Button>
              )}
            </div>
          ) : (
            <p className="text-gray-500 text-sm">No tags found</p>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
