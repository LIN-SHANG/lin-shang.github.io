---
title: Reading
summary: 读书笔记与随想
type: landing
_build:
  list: local

cascade:
  - target:
      path: '{/reading/*/**}'
    type: docs
    params:
      show_breadcrumb: true
      reading_section: true

sections:
  - block: collection
    id: reading
    content:
      title: 读书笔记
      subtitle: "在荒诞中寻找意义"
      count: 20
      filters:
        folders:
          - reading
        kinds:
          - section
    design:
      view: article-grid
      columns: 1
---
