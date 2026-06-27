"use client";

import { SlidersHorizontal } from "lucide-react";
import Link from "next/link";
import { useEffect, useState } from "react";
import type { RepositorySortMode } from "./repository-view-models";

type SortOption = {
  label: string;
  value: RepositorySortMode;
  href: string;
};

type RankingSortControlProps = {
  activeSort: RepositorySortMode;
  options: SortOption[];
};

export function RankingSortControl({ activeSort, options }: RankingSortControlProps) {
  const [selectedSort, setSelectedSort] = useState(activeSort);

  useEffect(() => {
    setSelectedSort(activeSort);
  }, [activeSort]);

  return (
    <div
      className="flex min-h-14 items-center gap-1.5 rounded-lg border border-[#244169] bg-[#10213d]/90 p-1.5 shadow-terminal"
      role="group"
      aria-label="榜单排序"
    >
      <span className="grid h-10 w-10 shrink-0 place-items-center text-muted" title="榜单排序">
        <SlidersHorizontal size={18} aria-hidden="true" />
      </span>
      <div className="grid min-w-0 flex-1 grid-cols-3 gap-1">
        {options.map((option) => (
          <Link
            key={option.value}
            href={option.href}
            aria-current={selectedSort === option.value ? "page" : undefined}
            onClick={() => setSelectedSort(option.value)}
            className={`inline-flex h-10 min-w-0 items-center justify-center rounded-md px-2 text-xs font-black transition ${
              selectedSort === option.value
                ? "bg-cyan text-[#071321] shadow-[0_0_16px_rgba(34,211,238,0.2)]"
                : "text-muted hover:bg-[#172b50] hover:text-ink"
            }`}
          >
            {option.label}
          </Link>
        ))}
      </div>
    </div>
  );
}
