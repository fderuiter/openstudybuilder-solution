<template>
  <div class="decision-timeline">
    <div class="timeline-container">
      <div v-for="log in sortedLogs" :key="log.key" class="timeline-item">
        <div class="timeline-icon">
          <span class="badge" :class="statusClass(log.frontmatter.status)">{{ log.frontmatter.status || 'Draft' }}</span>
        </div>
        <div class="timeline-content">
          <div class="timeline-header">
            <span class="timeline-date">{{ formatDate(log.frontmatter.date) }}</span>
            <span class="timeline-author" v-if="log.frontmatter.authors">by {{ log.frontmatter.authors }}</span>
          </div>
          <h3 class="timeline-title">
            <router-link :to="log.path">{{ log.title }}</router-link>
          </h3>
          <p class="timeline-description" v-if="log.frontmatter.description">
            {{ log.frontmatter.description }}
          </p>
          <div class="timeline-meta" v-if="log.frontmatter.impact">
            <strong>Impact Level:</strong> <span class="impact-badge" :class="log.frontmatter.impact.toLowerCase()">{{ log.frontmatter.impact }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'DecisionTimeline',
  computed: {
    sortedLogs() {
      if (!this.$site || !this.$site.pages) return [];
      
      return this.$site.pages
        .filter(page => {
          // Match files under /guides/decision-logs/ except the index (README) and template
          return page.path && (
            page.path.startsWith('/doc/guides/decision-logs/') ||
            page.path.startsWith('/guides/decision-logs/')
          ) && 
          !page.path.endsWith('README.html') && 
          !page.path.endsWith('template.html') &&
          page.frontmatter &&
          page.frontmatter.date;
        })
        .sort((a, b) => {
          const dateA = String(a.frontmatter.date);
          const dateB = String(b.frontmatter.date);
          return dateB.localeCompare(dateA);
        });
    }
  },
  methods: {
    formatDate(dateStr) {
      if (!dateStr) return '';
      const s = typeof dateStr === 'object' ? dateStr.toISOString().split('T')[0] : String(dateStr);
      const parts = s.split('-');
      if (parts.length < 3) return s;
      const year = parts[0];
      const monthIndex = parseInt(parts[1], 10) - 1;
      const day = parseInt(parts[2], 10);
      
      const months = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
      ];
      
      if (monthIndex >= 0 && monthIndex < 12) {
        return `${months[monthIndex]} ${day}, ${year}`;
      }
      return s;
    },
    statusClass(status) {
      if (!status) return 'draft';
      status = status.toLowerCase();
      if (status === 'approved') return 'approved';
      if (status === 'proposed') return 'proposed';
      if (status === 'rejected') return 'rejected';
      return 'draft';
    }
  }
}
</script>

<style scoped>
.decision-timeline {
  margin: 2rem 0;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Fira Sans", "Droid Sans", "Helvetica Neue", sans-serif;
}
.timeline-container {
  position: relative;
  padding-left: 2rem;
  border-left: 3px solid #dfe2e5;
}
.timeline-item {
  position: relative;
  margin-bottom: 2rem;
}
.timeline-item::before {
  content: "";
  position: absolute;
  left: -2.35rem;
  top: 0.25rem;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background-color: #3eaf7c;
  border: 3px solid #fff;
  box-shadow: 0 0 0 2px #3eaf7c;
}
.timeline-icon {
  margin-bottom: 0.5rem;
}
.timeline-content {
  background-color: #f8f9fa;
  border-radius: 6px;
  padding: 1.2rem;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  border: 1px solid #eaecef;
}
.timeline-header {
  font-size: 0.85rem;
  color: #6a8bad;
  margin-bottom: 0.5rem;
  display: flex;
  justify-content: space-between;
  flex-wrap: wrap;
}
.timeline-date {
  font-weight: 600;
}
.timeline-author {
  font-style: italic;
}
.timeline-title {
  margin-top: 0;
  margin-bottom: 0.5rem;
  font-size: 1.25rem;
}
.timeline-title a {
  color: #2c3e50;
  text-decoration: none;
}
.timeline-title a:hover {
  color: #3eaf7c;
}
.timeline-description {
  margin: 0 0 0.75rem 0;
  color: #4e6e8e;
  font-size: 0.95rem;
}
.timeline-meta {
  font-size: 0.85rem;
}
.badge {
  display: inline-block;
  padding: 0.25em 0.6em;
  font-size: 75%;
  font-weight: 700;
  line-height: 1;
  text-align: center;
  white-space: nowrap;
  vertical-align: baseline;
  border-radius: 0.25rem;
}
.badge.draft {
  background-color: #6c757d;
  color: #fff;
}
.badge.proposed {
  background-color: #007bff;
  color: #fff;
}
.badge.approved {
  background-color: #28a745;
  color: #fff;
}
.badge.rejected {
  background-color: #dc3545;
  color: #fff;
}
.impact-badge {
  text-transform: uppercase;
  font-weight: bold;
}
.impact-badge.high {
  color: #dc3545;
}
.impact-badge.medium {
  color: #ffc107;
}
.impact-badge.low {
  color: #28a745;
}
</style>
