"use client"

import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Category, Tag, BlogPost } from "@/lib/api"

interface SidebarProps {
  categories: Category[]
  tags: Tag[]
  allPosts: BlogPost[]
  selectedCategory: string | null
  selectedTag: string | null
  onCategoryClick: (categoryName: string) => void
  onTagClick: (tagName: string) => void
  onClearFilters: () => void
  setSelectedCategory: (category: string | null) => void
  setSelectedTag: (tag: string | null) => void
}

export function Sidebar({
  categories,
  tags,
  allPosts,
  selectedCategory,
  selectedTag,
  onCategoryClick,
  onTagClick,
  onClearFilters,
  setSelectedCategory,
  setSelectedTag
}: SidebarProps) {
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

      {/* Categories */}
      <Card>
        <CardContent className="p-4">
          <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
            📚 Categories
          </h3>
          <div className="space-y-2">
            {categories.map((category) => {
              const postCount = allPosts.filter(post => post.category_id === category.id).length
              return (
                <button
                  key={category.id}
                  onClick={() => onCategoryClick(category.name)}
                  className={`w-full text-left px-3 py-2 rounded-md text-sm transition-colors ${
                    selectedCategory === category.name
                      ? 'bg-blue-100 text-blue-700 font-medium'
                      : 'hover:bg-gray-100 text-gray-700'
                  }`}
                >
                  <div className="flex justify-between items-center">
                    <span>{category.name}</span>
                    <Badge variant="secondary" className="text-xs">
                      {postCount}
                    </Badge>
                  </div>
                </button>
              )
            })}
          </div>
        </CardContent>
      </Card>

      {/* Tags */}
      <Card>
        <CardContent className="p-4">
          <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
            🏷️ Tags
          </h3>
          <div className="flex flex-wrap gap-2">
            {tags.map((tag) => {
              const postCount = allPosts.filter(post => 
                post.tags.some(postTag => postTag.id === tag.id)
              ).length
              return (
                <button
                  key={tag.id}
                  onClick={() => onTagClick(tag.name)}
                  className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs transition-colors ${
                    selectedTag === tag.name
                      ? 'bg-blue-100 text-blue-700 font-medium'
                      : 'bg-gray-100 hover:bg-gray-200 text-gray-700'
                  }`}
                >
                  #{tag.name}
                  <Badge variant="secondary" className="text-xs ml-1">
                    {postCount}
                  </Badge>
                </button>
              )
            })}
          </div>
        </CardContent>
      </Card>

      {/* Clear Filters */}
      {(selectedCategory || selectedTag) && (
        <Card>
          <CardContent className="p-4">
            <div className="space-y-2">
              <h4 className="font-medium text-gray-900 text-sm">Active Filters:</h4>
              <div className="space-y-1">
                {selectedCategory && (
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">Category: <strong>{selectedCategory}</strong></span>
                    <button
                      onClick={() => setSelectedCategory(null)}
                      className="text-red-500 hover:text-red-700"
                    >
                      ✕
                    </button>
                  </div>
                )}
                {selectedTag && (
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">Tag: <strong>#{selectedTag}</strong></span>
                    <button
                      onClick={() => setSelectedTag(null)}
                      className="text-red-500 hover:text-red-700"
                    >
                      ✕
                    </button>
                  </div>
                )}
              </div>
              <Button
                onClick={onClearFilters}
                variant="outline"
                size="sm"
                className="w-full mt-2"
              >
                Clear All Filters
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
