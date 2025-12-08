#!/bin/bash
# Script to remove ALL GStreamer and libnice libraries from /usr/local/lib
# Use this before reinstalling/updating GStreamer

set -e

LIB_DIR="/usr/local/lib"

echo "=== Removing ALL GStreamer and libnice libraries from $LIB_DIR ==="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "ERROR: This script must be run as root (use sudo)"
    exit 1
fi

cd "$LIB_DIR"

# Count files before removal
GST_FILES=$(find . -maxdepth 1 \( -name "libgst*.so*" -o -name "libgst*.a" -o -name "libgst*.la" \) | wc -l)
NICE_FILES=$(find . -maxdepth 1 \( -name "libnice*.so*" -o -name "libnice*.a" -o -name "libnice*.la" \) | wc -l)
TOTAL_FILES=$((GST_FILES + NICE_FILES))
echo "Found $GST_FILES GStreamer library files to remove"
echo "Found $NICE_FILES libnice library files to remove"
echo "Total: $TOTAL_FILES files"
echo ""

# Confirm before proceeding
echo "WARNING: This will remove ALL GStreamer and libnice libraries, symlinks, and static libraries"
echo "Press Ctrl+C within 5 seconds to cancel..."
sleep 5
echo ""

# Step 1: Remove all GStreamer library files (shared, static, and libtool)
echo "Step 1: Removing all GStreamer library files..."
find . -maxdepth 1 \( -name "libgst*.so*" -o -name "libgst*.a" -o -name "libgst*.la" \) -delete
echo "Removed all GStreamer library files"
echo ""

# Step 1b: Remove all libnice library files
echo "Step 1b: Removing all libnice library files..."
find . -maxdepth 1 \( -name "libnice*.so*" -o -name "libnice*.a" -o -name "libnice*.la" \) -delete
echo "Removed all libnice library files"
echo ""

# Step 2: Remove GStreamer plugins directory
if [ -d "gstreamer-1.0" ]; then
    echo "Step 2: Removing GStreamer plugins directory..."
    rm -rf gstreamer-1.0
    echo "Removed gstreamer-1.0 plugin directory"
else
    echo "Step 2: No gstreamer-1.0 directory found"
fi
echo ""

# Step 3: Remove GStreamer pkg-config files
if [ -d "pkgconfig" ]; then
    echo "Step 3: Removing GStreamer pkg-config files..."
    PKGCONFIG_COUNT=$(find pkgconfig -name "gstreamer*.pc" | wc -l)
    if [ "$PKGCONFIG_COUNT" -gt 0 ]; then
        find pkgconfig -name "gstreamer*.pc" -delete
        echo "Removed $PKGCONFIG_COUNT GStreamer pkg-config files"
    else
        echo "No GStreamer pkg-config files found"
    fi
else
    echo "Step 3: No pkgconfig directory found"
fi
echo ""

# Step 4: Remove GStreamer GIR files (if any)
if [ -d "girepository-1.0" ]; then
    echo "Step 4: Removing GStreamer GIR files..."
    GIR_COUNT=$(find girepository-1.0 -name "Gst*.typelib" | wc -l)
    if [ "$GIR_COUNT" -gt 0 ]; then
        find girepository-1.0 -name "Gst*.typelib" -delete
        echo "Removed $GIR_COUNT GStreamer GIR files"
    else
        echo "No GStreamer GIR files found"
    fi
else
    echo "Step 4: No girepository-1.0 directory found"
fi
echo ""

# Step 5: Verify removal
echo "Step 5: Verifying removal..."
GST_REMAINING=$(find . -maxdepth 1 -name "libgst*" | wc -l)
NICE_REMAINING=$(find . -maxdepth 1 -name "libnice*" | wc -l)
TOTAL_REMAINING=$((GST_REMAINING + NICE_REMAINING))

if [ "$GST_REMAINING" -gt 0 ]; then
    echo "WARNING: $GST_REMAINING GStreamer files still remain:"
    find . -maxdepth 1 -name "libgst*"
else
    echo "SUCCESS: All GStreamer libraries removed"
fi

if [ "$NICE_REMAINING" -gt 0 ]; then
    echo "WARNING: $NICE_REMAINING libnice files still remain:"
    find . -maxdepth 1 -name "libnice*"
else
    echo "SUCCESS: All libnice libraries removed"
fi

if [ "$TOTAL_REMAINING" -eq 0 ]; then
    echo "SUCCESS: All libraries removed from $LIB_DIR"
fi
echo ""

# Step 6: Update ldconfig cache
echo "Step 6: Updating ldconfig cache..."
ldconfig
echo "ldconfig cache updated"
echo ""

echo "=== Cleanup complete ==="
echo ""
echo "Next steps:"
echo "1. Reinstall/update GStreamer using your build system"
echo "2. Run 'ldconfig' again after installation"
echo "3. Verify installation with: pkg-config --modversion gstreamer-1.0"
echo "4. Restart any running processes that use GStreamer"
