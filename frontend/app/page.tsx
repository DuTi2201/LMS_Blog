import { Suspense } from "react"
import { BlogList } from "@/components/blog-list"
import { Sidebar } from "@/components/sidebar"
import { Header } from "@/components/header"

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <div className="container mx-auto px-4 py-8">
        <div className="flex gap-8">
          <aside className="w-80 flex-shrink-0">
            <Sidebar />
          </aside>
          <main className="flex-1">
            <Suspense fallback={<div>Loading...</div>}>
              <BlogList />
            </Suspense>
          </main>
        </div>
      </div>
    </div>
  )
}
