from unittest.mock import MagicMock, patch
import pytest

from clinical_mdr_api.domain_repositories.syntax_templates.footnote_template_repository import (
    FootnoteTemplateRepository,
)


def test_footnote_template_repository_get_headers_passes_pagination_arguments():
    # given
    repo = FootnoteTemplateRepository()
    
    with patch.object(repo, "get_headers_optimized") as mock_optimized:
        mock_optimized.return_value = (["header1", "header2"], 2)
        
        # when
        results = repo.get_headers(
            field_name="name",
            status=None,
            search_string="test",
            filter_by=None,
            filter_operator=None,
            page_size=20,
            page_number=2,
            total_count=True,
        )
        
        # then
        mock_optimized.assert_called_once_with(
            field_name="name",
            status=None,
            search_string="test",
            filter_by=None,
            filter_operator=None,
            page_size=20,
            page_number=2,
            total_count=True,
        )
        assert results == (["header1", "header2"], 2)
