export interface CourseSummary {
  course_key: string;
  display_name: string;
  lms_link: string;
  number: string;
  org: string;
  rerun_link: string;
  run: string;
  url: string;
}

export interface CourseSummaryV4 extends CourseSummary {
  cms_link: string;
  is_active: boolean;
}

export interface LibrarySummary {
  library_key: string;
  display_name: string;
  org?: string;
  number?: string;
  url?: string;
  can_edit?: boolean;
  [key: string]: unknown;
}

export interface InProcessCourseAction {
  course_key?: string;
  display_name?: string;
  state?: string;
  [key: string]: unknown;
}

export interface HomeCoursesV3Response {
  courses: CourseSummary[];
  archived_courses: CourseSummary[];
  in_process_course_actions: InProcessCourseAction[];
}

export interface HomeLibrariesV3Response {
  libraries: LibrarySummary[];
}

export interface HomeContextV3Response extends HomeCoursesV3Response {
  libraries: LibrarySummary[];
  studio_name: string;
  studio_short_name?: string;
  platform_name?: string;
  user_is_active: boolean;
  allow_course_reruns?: boolean;
  allow_to_create_new_org?: boolean;
  allow_unicode_course_id?: boolean;
  allowed_organizations?: string[];
  [key: string]: unknown;
}

export interface PaginatedResponse<T> {
  count: number;
  num_pages: number;
  current_page: number;
  start: number;
  next: string | null;
  previous: string | null;
  results: T;
}

export interface HomeCoursesV4Results {
  courses: CourseSummaryV4[];
  in_process_course_actions: InProcessCourseAction[];
}

export type HomeCoursesV4Response = PaginatedResponse<HomeCoursesV4Results>;

export type CourseOrderingField = 'display_name' | 'org' | 'number' | 'run';

export type CourseOrdering = CourseOrderingField | `-${CourseOrderingField}`;

export interface HomeV3Params {
  org?: string;
}

export interface HomeLibrariesParams {
  org?: string;
  isMigrated?: boolean;
}

export interface HomeCoursesV4Params {
  org?: string;
  search?: string;
  ordering?: CourseOrdering;
  activeOnly?: boolean;
  archivedOnly?: boolean;
  page?: number;
  pageSize?: number;
}
