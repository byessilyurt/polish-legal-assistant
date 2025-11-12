'use client';

import { Category, CATEGORY_LABELS, CATEGORY_COLORS } from '@/types/legal-types';
import clsx from 'clsx';

interface CategoryFilterProps {
  selectedCategory: Category;
  onSelectCategory: (category: Category) => void;
}

export default function CategoryFilter({ selectedCategory, onSelectCategory }: CategoryFilterProps) {
  const categories = Object.values(Category);

  return (
    <div className="flex flex-wrap gap-2 p-4 bg-white border-b border-gray-200">
      {categories.map((category) => (
        <button
          key={category}
          onClick={() => onSelectCategory(category)}
          className={clsx(
            'px-4 py-2 rounded-full text-sm font-medium transition-all duration-200 transform hover:scale-105',
            selectedCategory === category
              ? 'ring-2 ring-primary-500 ring-offset-2'
              : '',
            CATEGORY_COLORS[category]
          )}
        >
          {CATEGORY_LABELS[category]}
        </button>
      ))}
    </div>
  );
}
