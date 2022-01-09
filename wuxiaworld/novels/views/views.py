from wuxiaworld.novels.views.bookmark_views import BookmarkSerializerView
from wuxiaworld.novels.views.chapter_views import SingleChapterSerializerView, ChaptersSerializerView
from wuxiaworld.novels.views.category_views import (CategorySerializerView, TagSerializerView,
                                        AuthorSerializerView)
from wuxiaworld.novels.views.profile_views import ProfileSerializerView
from wuxiaworld.novels.views.settings_views import SettingsSerializerView
from wuxiaworld.novels.views.novel_views import (SearchSerializerView,
             NovelSerializerView, GetAllNovelSerializerView)
from wuxiaworld.novels.views.util_views import (GoogleLogin, FacebookLogin, addNovels, addSources,
                    deleteDuplicate, deleteUnordered, siteMap, replace_images)
from wuxiaworld.novels.views.review_views import ReviewSerializerView
from wuxiaworld.novels.views.report_views import ReportSerializerView
from wuxiaworld.novels.views.announcement_views import AnnouncementSerializerView