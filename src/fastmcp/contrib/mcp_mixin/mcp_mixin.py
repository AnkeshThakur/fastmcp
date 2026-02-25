"""Provides a base mixin class and decorators for easy registration of class methods with FastMCP."""

import warnings
from collections.abc import Callable
from typing import TYPE_CHECKING, Any

import mcp.types
from mcp.types import Annotations, ToolAnnotations

import fastmcp
from fastmcp.prompts.prompt import Prompt
from fastmcp.resources.resource import Resource
from fastmcp.resources.template import ResourceTemplate
from fastmcp.server.auth.authorization import AuthCheck
from fastmcp.server.tasks import TaskConfig
from fastmcp.tools.tool import Tool
from fastmcp.utilities.types import get_fn_name

if TYPE_CHECKING:
    from fastmcp.server import FastMCP

_MCP_REGISTRATION_TOOL_ATTR = "_mcp_tool_registration"
_MCP_REGISTRATION_RESOURCE_ATTR = "_mcp_resource_registration"
_MCP_REGISTRATION_PROMPT_ATTR = "_mcp_prompt_registration"

_DEFAULT_SEPARATOR_TOOL = "_"
_DEFAULT_SEPARATOR_RESOURCE = "+"
_DEFAULT_SEPARATOR_PROMPT = "_"


def mcp_tool(
    name_or_fn: str | Callable[..., Any] | None = None,
    *,
    name: str | None = None,
    version: str | int | None = None,
    title: str | None = None,
    description: str | None = None,
    icons: list[mcp.types.Icon] | None = None,
    tags: set[str] | None = None,
    output_schema: dict[str, Any] | None = None,
    annotations: ToolAnnotations | dict[str, Any] | None = None,
    exclude_args: list[str] | None = None,
    serializer: Callable[[Any], str] | None = None,  # Deprecated
    meta: dict[str, Any] | None = None,
    enabled: bool = True,
    task: bool | TaskConfig | None = None,
    timeout: float | None = None,
    auth: AuthCheck | list[AuthCheck] | None = None,
) -> Callable[[Callable[..., Any]], Callable[..., Any]] | Callable[..., Any]:
    """Decorator to mark a method as an MCP tool for later registration.

    Args:
        name: Custom name for the tool (defaults to function name).
        version: Version of the tool.
        title: Title for the tool.
        description: Description of what the tool does.
        icons: List of icons for the tool.
        tags: Set of tags to categorize the tool.
        output_schema: JSON schema for the tool's output.
        annotations: Tool annotations for additional metadata.
        exclude_args: List of function arguments to exclude from the tool schema.
        serializer: (Deprecated) Custom serializer for tool results.
        meta: Additional metadata dictionary.
        enabled: Whether the tool is enabled (default True).
        task: Task configuration for background execution.
        timeout: Timeout for tool execution.
        auth: Authorization checks for this tool.
    """
    import inspect

    if serializer is not None and fastmcp.settings.deprecation_warnings:
        warnings.warn(
            "The `serializer` parameter is deprecated. "
            "Return ToolResult from your tools for full control over serialization. "
            "See https://gofastmcp.com/servers/tools#custom-serialization for migration examples.",
            DeprecationWarning,
            stacklevel=2,
        )

    def decorator(
        func: Callable[..., Any], tool_name: str | None
    ) -> Callable[..., Any]:
        call_args = {
            "name": tool_name or get_fn_name(func),
            "version": version,
            "title": title,
            "description": description,
            "icons": icons,
            "tags": tags,
            "output_schema": output_schema,
            "annotations": annotations,
            "exclude_args": exclude_args,
            "serializer": serializer,
            "meta": meta,
            "enabled": enabled,
            "task": task,
            "timeout": timeout,
            "auth": auth,
        }
        call_args = {k: v for k, v in call_args.items() if v is not None}
        setattr(func, _MCP_REGISTRATION_TOOL_ATTR, call_args)
        return func

    # Handle direct decoration (@mcp_tool)
    if inspect.isroutine(name_or_fn):
        return decorator(name_or_fn, name)

    # Handle string name (@mcp_tool("custom_name"))
    elif isinstance(name_or_fn, str):
        if name is not None:
            raise TypeError("Cannot specify name both as first argument and keyword")
        tool_name = name_or_fn

    # Handle parameterized decoration (@mcp_tool() or @mcp_tool(auth=...))
    elif name_or_fn is None:
        tool_name = name
    else:
        raise TypeError(f"Invalid first argument: {type(name_or_fn)}")

    # Return decorator factory
    def wrapper(func: Callable[..., Any]) -> Callable[..., Any]:
        return decorator(func, tool_name)

    return wrapper


def mcp_resource(
    uri: str,
    *,
    name: str | None = None,
    version: str | int | None = None,
    title: str | None = None,
    description: str | None = None,
    icons: list[mcp.types.Icon] | None = None,
    mime_type: str | None = None,
    tags: set[str] | None = None,
    annotations: Annotations | None = None,
    meta: dict[str, Any] | None = None,
    enabled: bool = True,
    task: bool | TaskConfig | None = None,
    auth: AuthCheck | list[AuthCheck] | None = None,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator to mark a method as an MCP resource for later registration.

    Args:
        uri: URI for the resource.
        name: Custom name for the resource (defaults to function name).
        version: Version of the resource.
        title: Title for the resource.
        description: Description of what the resource provides.
        icons: List of icons for the resource.
        mime_type: MIME type for the resource.
        tags: Set of tags to categorize the resource.
        annotations: Resource annotations for additional metadata.
        meta: Additional metadata dictionary.
        enabled: Whether the resource is enabled (default True).
        task: Task configuration for background execution.
        auth: Authorization checks for this resource.
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        call_args = {
            "uri": uri,
            "name": name or get_fn_name(func),
            "version": version,
            "title": title,
            "description": description,
            "icons": icons,
            "mime_type": mime_type,
            "tags": tags,
            "annotations": annotations,
            "meta": meta,
            "enabled": enabled,
            "task": task,
            "auth": auth,
        }
        call_args = {k: v for k, v in call_args.items() if v is not None}

        setattr(func, _MCP_REGISTRATION_RESOURCE_ATTR, call_args)

        return func

    return decorator


def mcp_prompt(
    name_or_fn: str | Callable[..., Any] | None = None,
    *,
    name: str | None = None,
    version: str | int | None = None,
    title: str | None = None,
    description: str | None = None,
    icons: list[mcp.types.Icon] | None = None,
    tags: set[str] | None = None,
    meta: dict[str, Any] | None = None,
    enabled: bool = True,
    task: bool | TaskConfig | None = None,
    auth: AuthCheck | list[AuthCheck] | None = None,
) -> Callable[[Callable[..., Any]], Callable[..., Any]] | Callable[..., Any]:
    """Decorator to mark a method as an MCP prompt for later registration.

    Args:
        name: Custom name for the prompt (defaults to function name).
        version: Version of the prompt.
        title: Title for the prompt.
        description: Description of what the prompt does.
        icons: List of icons for the prompt.
        tags: Set of tags to categorize the prompt.
        meta: Additional metadata dictionary.
        enabled: Whether the prompt is enabled (default True).
        task: Task configuration for background execution.
        auth: Authorization checks for this prompt.
    """
    import inspect

    def decorator(
        func: Callable[..., Any], prompt_name: str | None
    ) -> Callable[..., Any]:
        call_args = {
            "name": prompt_name or get_fn_name(func),
            "version": version,
            "title": title,
            "description": description,
            "icons": icons,
            "tags": tags,
            "meta": meta,
            "enabled": enabled,
            "task": task,
            "auth": auth,
        }
        call_args = {k: v for k, v in call_args.items() if v is not None}
        setattr(func, _MCP_REGISTRATION_PROMPT_ATTR, call_args)
        return func

    # Handle direct decoration (@mcp_prompt)
    if inspect.isroutine(name_or_fn):
        return decorator(name_or_fn, name)

    # Handle string name (@mcp_prompt("custom_name"))
    elif isinstance(name_or_fn, str):
        if name is not None:
            raise TypeError("Cannot specify name both as first argument and keyword")
        prompt_name = name_or_fn

    # Handle parameterized decoration (@mcp_prompt() or @mcp_prompt(auth=...))
    elif name_or_fn is None:
        prompt_name = name
    else:
        raise TypeError(f"Invalid first argument: {type(name_or_fn)}")

    # Return decorator factory
    def wrapper(func: Callable[..., Any]) -> Callable[..., Any]:
        return decorator(func, prompt_name)

    return wrapper


class MCPMixin:
    """Base mixin class for objects that can register tools, resources, and prompts
    with a FastMCP server instance using decorators.

    This mixin provides methods like `register_all`, `register_tools`, etc.,
    which iterate over the methods of the inheriting class, find methods
    decorated with `@mcp_tool`, `@mcp_resource`, or `@mcp_prompt`, and
    register them with the provided FastMCP server instance.
    """

    def _get_methods_to_register(self, registration_type: str):
        """Retrieves all methods marked for a specific registration type."""
        return [
            (
                getattr(self, method_name),
                getattr(getattr(self, method_name), registration_type).copy(),
            )
            for method_name in dir(self)
            if callable(getattr(self, method_name))
            and hasattr(getattr(self, method_name), registration_type)
        ]

    def register_tools(
        self,
        mcp_server: "FastMCP",
        prefix: str | None = None,
        separator: str = _DEFAULT_SEPARATOR_TOOL,
    ) -> None:
        """Registers all methods marked with @mcp_tool with the FastMCP server.

        Args:
            mcp_server: The FastMCP server instance to register tools with.
            prefix: Optional prefix to prepend to tool names. If provided, the
                final name will be f"{prefix}{separator}{original_name}".
            separator: The separator string used between prefix and original name.
                Defaults to '_'.
        """
        for method, registration_info in self._get_methods_to_register(
            _MCP_REGISTRATION_TOOL_ATTR
        ):
            if prefix:
                registration_info["name"] = (
                    f"{prefix}{separator}{registration_info['name']}"
                )

            tool = Tool.from_function(
                fn=method,
                name=registration_info.get("name"),
                version=registration_info.get("version"),
                title=registration_info.get("title"),
                description=registration_info.get("description"),
                icons=registration_info.get("icons"),
                tags=registration_info.get("tags"),
                output_schema=registration_info.get("output_schema"),
                annotations=registration_info.get("annotations"),
                exclude_args=registration_info.get("exclude_args"),
                serializer=registration_info.get("serializer"),
                meta=registration_info.get("meta"),
                task=registration_info.get("task"),
                timeout=registration_info.get("timeout"),
                auth=registration_info.get("auth"),
            )

            mcp_server.add_tool(tool)

    def register_resources(
        self,
        mcp_server: "FastMCP",
        prefix: str | None = None,
        separator: str = _DEFAULT_SEPARATOR_RESOURCE,
    ) -> None:
        """Registers all methods marked with @mcp_resource with the FastMCP server.

        Args:
            mcp_server: The FastMCP server instance to register resources with.
            prefix: Optional prefix to prepend to resource names and URIs. If provided,
                the final name will be f"{prefix}{separator}{original_name}" and the
                final URI will be f"{prefix}{separator}{original_uri}".
            separator: The separator string used between prefix and original name/URI.
                Defaults to '+'.
        """
        for method, registration_info in self._get_methods_to_register(
            _MCP_REGISTRATION_RESOURCE_ATTR
        ):
            if prefix:
                registration_info["name"] = (
                    f"{prefix}{separator}{registration_info['name']}"
                )
                registration_info["uri"] = (
                    f"{prefix}{separator}{registration_info['uri']}"
                )

            # Check if we need to create a template or regular resource
            uri = registration_info["uri"]
            has_uri_params = "{" in uri and "}" in uri

            if has_uri_params:
                resource = ResourceTemplate.from_function(
                    fn=method,
                    uri_template=registration_info["uri"],
                    name=registration_info.get("name"),
                    version=registration_info.get("version"),
                    title=registration_info.get("title"),
                    description=registration_info.get("description"),
                    icons=registration_info.get("icons"),
                    mime_type=registration_info.get("mime_type"),
                    tags=registration_info.get("tags"),
                    annotations=registration_info.get("annotations"),
                    meta=registration_info.get("meta"),
                    task=registration_info.get("task"),
                    auth=registration_info.get("auth"),
                )
                mcp_server.add_template(resource)
            else:
                resource = Resource.from_function(
                    fn=method,
                    uri=registration_info["uri"],
                    name=registration_info.get("name"),
                    version=registration_info.get("version"),
                    title=registration_info.get("title"),
                    description=registration_info.get("description"),
                    icons=registration_info.get("icons"),
                    mime_type=registration_info.get("mime_type"),
                    tags=registration_info.get("tags"),
                    annotations=registration_info.get("annotations"),
                    meta=registration_info.get("meta"),
                    task=registration_info.get("task"),
                )
                mcp_server.add_resource(resource)

    def register_prompts(
        self,
        mcp_server: "FastMCP",
        prefix: str | None = None,
        separator: str = _DEFAULT_SEPARATOR_PROMPT,
    ) -> None:
        """Registers all methods marked with @mcp_prompt with the FastMCP server.

        Args:
            mcp_server: The FastMCP server instance to register prompts with.
            prefix: Optional prefix to prepend to prompt names. If provided, the
                final name will be f"{prefix}{separator}{original_name}".
            separator: The separator string used between prefix and original name.
                Defaults to '_'.
        """
        for method, registration_info in self._get_methods_to_register(
            _MCP_REGISTRATION_PROMPT_ATTR
        ):
            if prefix:
                registration_info["name"] = (
                    f"{prefix}{separator}{registration_info['name']}"
                )
            prompt = Prompt.from_function(
                fn=method,
                name=registration_info.get("name"),
                version=registration_info.get("version"),
                title=registration_info.get("title"),
                description=registration_info.get("description"),
                icons=registration_info.get("icons"),
                tags=registration_info.get("tags"),
                meta=registration_info.get("meta"),
                task=registration_info.get("task"),
                auth=registration_info.get("auth"),
            )
            mcp_server.add_prompt(prompt)

    def register_all(
        self,
        mcp_server: "FastMCP",
        prefix: str | None = None,
        tool_separator: str = _DEFAULT_SEPARATOR_TOOL,
        resource_separator: str = _DEFAULT_SEPARATOR_RESOURCE,
        prompt_separator: str = _DEFAULT_SEPARATOR_PROMPT,
    ) -> None:
        """Registers all marked tools, resources, and prompts with the server.

        This method calls `register_tools`, `register_resources`, and `register_prompts`
        internally, passing the provided prefix and separators.

        Args:
            mcp_server: The FastMCP server instance to register with.
            prefix: Optional prefix applied to all registered items unless overridden
                by a specific separator argument.
            tool_separator: Separator for tool names (defaults to '_').
            resource_separator: Separator for resource names/URIs (defaults to '+').
            prompt_separator: Separator for prompt names (defaults to '_').
        """
        self.register_tools(mcp_server, prefix=prefix, separator=tool_separator)
        self.register_resources(mcp_server, prefix=prefix, separator=resource_separator)
        self.register_prompts(mcp_server, prefix=prefix, separator=prompt_separator)
