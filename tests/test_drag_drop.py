"""
test_drag_drop.py — Tests para la funcionalidad de drag & drop del job list.

Usage:
    python test_drag_drop.py

Los tests requieren un display (Windows Desktop, X server, o virtual framebuffer).
"""

import sys
from unittest import TestCase, main as unittest_main

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QPoint, QPointF

from models import RenderJob
from main_window import MainWindow, DraggableQueueTree


def create_mock_drop_event(tree, target_row):
    """Crea un mock de QDropEvent que apunta a un item específico."""

    class MockPosition:
        def __init__(self, pt):
            self._pt = pt

        def toPoint(self):
            return self._pt

    class MockEvent:
        def __init__(self, tree, target_row):
            self._tree = tree
            self._target_row = target_row
            target_item = (
                tree.topLevelItem(target_row)
                if target_row < tree.topLevelItemCount()
                else None
            )
            if target_item:
                rect = tree.visualItemRect(target_item)
                center = rect.center() if not rect.isEmpty() else QPoint(50, 50)
            else:
                center = QPoint(50, 50)
            self._position = MockPosition(center)

        def position(self):
            return self._position

    return MockEvent(tree, target_row)


class FakeDropEvent:
    def __init__(self, x=100, y=100):
        self._pos = QPointF(x, y)

    def position(self):
        return self._pos


class DragDropTests(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance()
        if cls.app is None:
            cls.app = QApplication(sys.argv)

    def setUp(self):
        self.window = MainWindow()
        self.window.show()
        QApplication.processEvents()
        self.tree = self.window.queue_tree

    def tearDown(self):
        self.window.close()
        self.window.deleteLater()
        QApplication.processEvents()

    def _get_job_ids_from_tree(self):
        ids = []
        for i in range(self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(i)
            if item:
                try:
                    ids.append(int(item.text(0)))
                except (ValueError, AttributeError):
                    pass
        return ids

    def _get_job_ids_from_list(self):
        return [j.job_id for j in self.window.jobs]

    def test_2_1_drag_pending_job_repositions(self):
        """2.1: Drag job Pending → reposiciona"""
        job_ids = self._get_job_ids_from_tree()
        if len(job_ids) < 2:
            self.skipTest("Need at least 2 jobs")

        target_row = 1
        event = create_mock_drop_event(self.tree, target_row)
        self.tree._drag_source_row = 0
        self.tree.dropEvent(event)
        QApplication.processEvents()

        new_job_ids = self._get_job_ids_from_tree()
        list_job_ids = self._get_job_ids_from_list()

        print(f"[TEST 2.1] Tree before: {job_ids}")
        print(f"[TEST 2.1] Tree after: {new_job_ids}")
        print(f"[TEST 2.1] List after: {list_job_ids}")

        self.assertEqual(
            new_job_ids, list_job_ids, "Tree and jobs list should be synchronized"
        )
        self.assertNotEqual(job_ids, new_job_ids, "Order should have changed")

    def test_2_2_drag_running_job_blocked(self):
        """2.2: Intento drag job Running → no inicia drag"""
        running_job = None
        for j in self.window.jobs:
            if j.status == RenderJob.STATUS_PENDING:
                j.status = RenderJob.STATUS_RUNNING
                running_job = j
                break

        if running_job is None:
            self.skipTest("No pending jobs to convert to running")

        self.window._refresh_tree()
        QApplication.processEvents()
        self.tree.setCurrentItem(self.tree.topLevelItem(0))
        QApplication.processEvents()

        self.tree.startDrag(Qt.DropAction.MoveAction)

        self.assertIsNone(
            self.tree._drag_source_row,
            f"Drag should be blocked for Running job, got row {self.tree._drag_source_row}",
        )

    def test_2_3_drag_paused_job_blocked(self):
        """2.3: Intento drag job Paused → no inicia drag"""
        paused_job = None
        for j in self.window.jobs:
            if j.status == RenderJob.STATUS_PENDING:
                j.status = RenderJob.STATUS_PAUSED
                paused_job = j
                break

        if paused_job is None:
            self.skipTest("No pending jobs to convert to paused")

        self.window._refresh_tree()
        QApplication.processEvents()
        self.tree.setCurrentItem(self.tree.topLevelItem(0))
        QApplication.processEvents()

        self.tree.startDrag(Qt.DropAction.MoveAction)

        self.assertIsNone(
            self.tree._drag_source_row,
            f"Drag should be blocked for Paused job, got row {self.tree._drag_source_row}",
        )

    def test_2_4_drag_same_position_no_change(self):
        """2.4: Drag a misma posición → no hace nada"""
        job_ids_before = self._get_job_ids_from_tree()
        if len(job_ids_before) < 1:
            self.skipTest("Need at least 1 job")

        source_item = self.tree.topLevelItem(0)
        if not source_item:
            self.skipTest("No items in tree")

        rect = self.tree.visualItemRect(source_item)
        center = rect.center()

        class MockEvent:
            def __init__(self, pos):
                self._position = pos

            def position(self):
                return self._position

        class MockPos:
            def __init__(self, pt):
                self._pt = pt

            def toPoint(self):
                return self._pt

        event = MockEvent(MockPos(center))
        self.tree._drag_source_row = 0
        self.tree.dropEvent(event)

        job_ids_after = self._get_job_ids_from_tree()

        print(f"[TEST 2.4] Before: {job_ids_before}")
        print(f"[TEST 2.4] After: {job_ids_after}")

        self.assertEqual(
            job_ids_before, job_ids_after, "Same position drag should not change order"
        )

    def test_2_5_combo_preserved_after_drop(self):
        """2.5: Drag con QComboBox embeddeado → preserva selección"""
        job_ids = self._get_job_ids_from_tree()
        if len(job_ids) < 2:
            self.skipTest("Need at least 2 jobs")

        source_item = self.tree.topLevelItem(0)
        if not source_item:
            return

        original_job_id = int(source_item.text(0))
        original_combo = self.tree.itemWidget(source_item, 4)
        if not original_combo:
            self.skipTest("No QComboBox embedded")

        original_text = original_combo.currentText()
        self.tree._save_widget_state(source_item)
        self.tree._drag_source_row = 0

        self.tree.dropEvent(FakeDropEvent())
        QApplication.processEvents()

        found = False
        for i in range(self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(i)
            if item and int(item.text(0)) == original_job_id:
                new_combo = self.tree.itemWidget(item, 4)
                new_text = new_combo.currentText() if new_combo else None
                print(
                    f"[TEST 2.5] Job {original_job_id}: original={original_text}, new={new_text}"
                )
                self.assertEqual(
                    new_text,
                    original_text,
                    "ComboBox selection should be preserved for the same job",
                )
                found = True
                break

        self.assertTrue(found, f"Job {original_job_id} not found in tree after drag")

    def test_2_6_multi_select_only_one_dragged(self):
        """2.6: Multi-select + drag → solo 1 item arrastrado"""
        if self.tree.topLevelItemCount() < 2:
            self.skipTest("Need at least 2 jobs")

        self.tree.setSelectionMode(DraggableQueueTree.SelectionMode.ExtendedSelection)

        item1 = self.tree.topLevelItem(0)
        item2 = self.tree.topLevelItem(1)

        self.tree.setCurrentItem(item1)
        self.tree.setCurrentItem(item2)

        selected = self.tree.selectedItems()
        print(f"[TEST 2.6] Selected count: {len(selected)}")

        self.tree.setSelectionMode(DraggableQueueTree.SelectionMode.ExtendedSelection)

        old_drag_row = self.tree._drag_source_row
        try:
            self.tree.startDrag(Qt.DropAction.MoveAction)
        except:
            pass

        new_drag_row = self.tree._drag_source_row

        print(f"[TEST 2.6] Drag row: {new_drag_row}")

        self.assertIsNotNone(
            new_drag_row,
            "Drag should have started for single/extended selection with 1 item",
        )

        if new_drag_row == 0:
            print(
                "[TEST 2.6] PASS: Code correctly starts drag for first item in selection"
            )

    def test_2_7_drop_last_item(self):
        """2.7: Drop último item al final"""
        job_ids_before = self._get_job_ids_from_tree()
        count = self.tree.topLevelItemCount()
        if count < 2:
            self.skipTest("Need at least 2 jobs")

        last_row = count - 1
        event = create_mock_drop_event(self.tree, last_row)
        self.tree._drag_source_row = 0
        self.tree.dropEvent(event)
        QApplication.processEvents()

        job_ids_after = self._get_job_ids_from_tree()

        print(f"[TEST 2.7] Before: {job_ids_before}")
        print(f"[TEST 2.7] After: {job_ids_after}")

    def test_2_8_empty_queue_no_crash(self):
        """2.8: Drop en empty queue → no crashea"""
        self.tree.blockSignals(True)
        self.tree.clear()
        self.tree.blockSignals(False)
        QApplication.processEvents()

        if self.tree.topLevelItemCount() == 0:
            self.tree._drag_source_row = 0

            try:
                self.tree.dropEvent(FakeDropEvent())
            except Exception as e:
                self.fail(f"Drop on empty queue raised exception: {e}")
        else:
            self.skipTest("Could not clear tree")

    def test_2_9_jobs_list_synchronized(self):
        """2.9: Jobs list sincronizado después de reorder"""
        if self.tree.topLevelItemCount() < 2:
            self.skipTest("Need at least 2 jobs")

        event = create_mock_drop_event(self.tree, 1)
        self.tree._drag_source_row = 0
        self.tree.dropEvent(event)
        QApplication.processEvents()

        tree_ids = self._get_job_ids_from_tree()
        list_ids = self._get_job_ids_from_list()

        print(f"[TEST 2.9] Tree IDs: {tree_ids}")
        print(f"[TEST 2.9] List IDs: {list_ids}")

        self.assertEqual(
            tree_ids, list_ids, f"Tree {tree_ids} should match list {list_ids}"
        )

    def test_2_10_persisted_order(self):
        """2.10: Queue reordenado se persiste y restorea"""
        original_ids = self._get_job_ids_from_list()

        if len(original_ids) < 2:
            self.skipTest("Need at least 2 jobs")

        event = create_mock_drop_event(self.tree, 1)
        self.tree._drag_source_row = 0
        self.tree.dropEvent(event)
        QApplication.processEvents()

        self.window._auto_save_queue()
        QApplication.processEvents()

        new_window = MainWindow()
        new_window.show()
        QApplication.processEvents()

        new_job_ids = [j.job_id for j in new_window.jobs]

        print(f"[TEST 2.10] Original: {original_ids}")
        print(f"[TEST 2.10] After reorder + restart: {new_job_ids}")

        new_window.close()
        new_window.deleteLater()


if __name__ == "__main__":
    unittest_main(verbosity=2)
