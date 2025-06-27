// 時間割アプリのメインJavaScriptファイル

class TimetableApp {
    constructor() {
        this.subjects = [];
        this.showDetails = false;
        this.currentSubject = null;
        this.draggedSubject = null;
        this.init();
    }

    // アプリケーションの初期化
    init() {
        this.loadSubjects();
        this.setupEventListeners();
        this.renderTimetable();
        this.setupModal();
    }

    // イベントリスナーの設定
    setupEventListeners() {
        // 科目追加フォームのイベント
        const addForm = document.getElementById('addSubjectForm');
        if (addForm) {
            addForm.addEventListener('submit', (e) => this.handleAddSubject(e));
        }

        // 詳細表示切り替えボタン
        const toggleDetailsBtn = document.getElementById('toggleDetails');
        if (toggleDetailsBtn) {
            toggleDetailsBtn.addEventListener('click', () => this.toggleDetailsView());
        }
    }

    // モーダルの設定
    setupModal() {
        const modal = document.getElementById('subjectModal');
        const closeBtn = document.querySelector('.close');
        const closeModalBtn = document.getElementById('closeModalBtn');
        const deleteSubjectBtn = document.getElementById('deleteSubjectBtn');

        // モーダルを閉じる
        const closeModal = () => {
            modal.style.display = 'none';
            this.currentSubject = null;
            // モーダルを閉じた後にbodyクラスを削除
            document.body.classList.remove('modal-open');
        };

        // イベントリスナー
        closeBtn.addEventListener('click', closeModal);
        closeModalBtn.addEventListener('click', closeModal);
        deleteSubjectBtn.addEventListener('click', () => this.deleteCurrentSubject());

        // モーダル外クリックで閉じる
        window.addEventListener('click', (e) => {
            if (e.target === modal) {
                closeModal();
            }
        });

        // ESCキーで閉じる
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && modal.style.display === 'block') {
                closeModal();
            }
        });
    }

    // 現在の科目を削除
    async deleteCurrentSubject() {
        if (this.currentSubject) {
            await this.deleteSubject(this.currentSubject.id);
            document.getElementById('subjectModal').style.display = 'none';
            // モーダルを閉じた後にbodyクラスを削除
            document.body.classList.remove('modal-open');
        }
    }

    // 詳細表示の切り替え
    toggleDetailsView() {
        this.showDetails = !this.showDetails;
        const toggleBtn = document.getElementById('toggleDetails');
        if (toggleBtn) {
            toggleBtn.textContent = this.showDetails ? '簡易表示' : '詳細表示';
        }
        this.renderSubjectsList();
    }

    // 科目一覧をサーバーから取得
    async loadSubjects() {
        try {
            const response = await fetch('/api/subjects');
            if (response.ok) {
                this.subjects = await response.json();
                this.renderSubjectsList();
                this.renderTimetable();
            } else {
                this.showMessage('科目の読み込みに失敗しました', 'error');
            }
        } catch (error) {
            console.error('科目の読み込みエラー:', error);
            this.showMessage('科目の読み込みに失敗しました', 'error');
        }
    }

    // 新しい科目を追加
    async handleAddSubject(event) {
        event.preventDefault();
        
        const formData = new FormData(event.target);
        const subjectData = {
            name: formData.get('name'),
            day: formData.get('day'),
            period: formData.get('period'),
            room: formData.get('room') || '',
            credits: formData.get('credits') || null,
            teacher: formData.get('teacher') || '',
            evaluation: formData.get('evaluation') || '',
            style: formData.get('style') || '',
            description: formData.get('description') || '',
            memo: formData.get('memo') || '',
            ease: formData.get('ease') || null
        };

        // バリデーション
        if (!subjectData.name || !subjectData.day || !subjectData.period) {
            this.showMessage('科目名、曜日、時限は必須項目です', 'error');
            return;
        }

        // 同じ時間帯に既に科目があるかチェック
        const existingSubject = this.subjects.find(subject => 
            subject.day === subjectData.day && subject.period === subjectData.period
        );

        if (existingSubject) {
            this.showMessage(`${subjectData.day}曜日${subjectData.period}限には既に「${existingSubject.name}」が登録されています`, 'error');
            return;
        }

        try {
            const response = await fetch('/api/subjects', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(subjectData)
            });

            if (response.ok) {
                this.showMessage('科目が正常に追加されました', 'success');
                event.target.reset();
                await this.loadSubjects(); // 科目一覧を再読み込み
            } else {
                const errorData = await response.json();
                this.showMessage(errorData.error || '科目の追加に失敗しました', 'error');
            }
        } catch (error) {
            console.error('科目追加エラー:', error);
            this.showMessage('科目の追加に失敗しました', 'error');
        }
    }

    // 科目を削除
    async deleteSubject(subjectId) {
        if (!confirm('この科目を削除しますか？')) {
            return;
        }

        try {
            const response = await fetch(`/api/subjects/${subjectId}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                this.showMessage('科目が正常に削除されました', 'success');
                await this.loadSubjects(); // 科目一覧を再読み込み
            } else {
                this.showMessage('科目の削除に失敗しました', 'error');
            }
        } catch (error) {
            console.error('科目削除エラー:', error);
            this.showMessage('科目の削除に失敗しました', 'error');
        }
    }

    // 科目を移動
    async moveSubject(subjectId, newDay, newPeriod) {
        try {
            const response = await fetch(`/api/subjects/${subjectId}/move`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    day: newDay,
                    period: newPeriod
                })
            });

            if (response.ok) {
                this.showMessage('科目が正常に移動されました', 'success');
                await this.loadSubjects();
            } else {
                this.showMessage('科目の移動に失敗しました', 'error');
            }
        } catch (error) {
            console.error('科目移動エラー:', error);
            this.showMessage('科目の移動に失敗しました', 'error');
        }
    }

    // 科目一覧を表示
    renderSubjectsList() {
        const subjectsList = document.getElementById('subjectsList');
        if (!subjectsList) return;

        if (this.subjects.length === 0) {
            subjectsList.innerHTML = '<p class="loading">登録されている科目はありません</p>';
            return;
        }

        subjectsList.innerHTML = this.subjects.map(subject => {
            if (this.showDetails) {
                return this.renderDetailedSubject(subject);
            } else {
                return this.renderSimpleSubject(subject);
            }
        }).join('');
    }

    // 簡易表示の科目アイテム
    renderSimpleSubject(subject) {
        return `
            <div class="subject-item">
                <div class="subject-info">
                    <span class="subject-name">${this.escapeHtml(subject.name)}</span>
                    <span class="subject-details">${subject.day}曜日 ${subject.period}限</span>
                </div>
                <button class="btn btn-danger" onclick="app.deleteSubject(${subject.id})">
                    削除
                </button>
            </div>
        `;
    }

    // 詳細表示の科目アイテム
    renderDetailedSubject(subject) {
        const details = [];
        
        if (subject.room) details.push(['教室', subject.room]);
        if (subject.credits) details.push(['単位数', `${subject.credits}単位`]);
        if (subject.teacher) details.push(['教員', subject.teacher]);
        if (subject.evaluation) details.push(['評価割合', subject.evaluation]);
        if (subject.style) details.push(['授業形態', subject.style]);
        if (subject.ease) details.push(['楽さ', `${subject.ease}/5`]);
        if (subject.description) details.push(['授業内容', subject.description]);
        if (subject.memo) details.push(['メモ', subject.memo]);

        const detailsHTML = details.length > 0 ? `
            <div class="subject-details-grid">
                ${details.map(([label, value]) => `
                    <div class="subject-detail-item">
                        <span class="subject-detail-label">${label}</span>
                        <span class="subject-detail-value">${this.escapeHtml(value)}</span>
                    </div>
                `).join('')}
            </div>
        ` : '';

        return `
            <div class="subject-item detailed">
                <div class="subject-info detailed">
                    <div>
                        <span class="subject-name">${this.escapeHtml(subject.name)}</span>
                        <span class="subject-details">${subject.day}曜日 ${subject.period}限</span>
                    </div>
                    ${detailsHTML}
                </div>
                <div class="subject-actions">
                    <button class="btn btn-danger" onclick="app.deleteSubject(${subject.id})">
                        削除
                    </button>
                </div>
            </div>
        `;
    }

    // 時間割テーブルを表示
    renderTimetable() {
        const timetableBody = document.getElementById('timetableBody');
        if (!timetableBody) return;

        const days = ['月', '火', '水', '木', '金', '土']; // 日曜日を削除
        const periods = 6;

        let tableHTML = '';
        
        for (let period = 1; period <= periods; period++) {
            tableHTML += '<tr>';
            tableHTML += `<td><strong>${period}限</strong></td>`;
            
            for (const day of days) {
                const subject = this.subjects.find(s => s.day === day && s.period === period.toString());
                
                if (subject) {
                    const tooltip = this.createTooltipText(subject);
                    tableHTML += `<td class="has-subject" 
                        data-subject-id="${subject.id}"
                        data-day="${day}"
                        data-period="${period}"
                        title="${tooltip}">
                        ${this.escapeHtml(subject.name)}
                    </td>`;
                } else {
                    tableHTML += `<td data-day="${day}" data-period="${period}"></td>`;
                }
            }
            
            tableHTML += '</tr>';
        }

        timetableBody.innerHTML = tableHTML;
        this.setupTimetableEvents();
    }

    // 時間割のイベント設定
    setupTimetableEvents() {
        const cells = document.querySelectorAll('.timetable td');
        
        cells.forEach(cell => {
            // クリックイベント（詳細表示）
            cell.addEventListener('click', (e) => {
                if (cell.classList.contains('has-subject')) {
                    const subjectId = cell.dataset.subjectId;
                    const subject = this.subjects.find(s => s.id == subjectId);
                    if (subject) {
                        this.showSubjectModal(subject);
                    }
                }
            });

            // ドラッグ&ドロップ
            if (cell.classList.contains('has-subject')) {
                cell.draggable = true;
                
                cell.addEventListener('dragstart', (e) => {
                    this.draggedSubject = {
                        id: cell.dataset.subjectId,
                        day: cell.dataset.day,
                        period: cell.dataset.period
                    };
                    cell.classList.add('dragging');
                });

                cell.addEventListener('dragend', (e) => {
                    cell.classList.remove('dragging');
                    this.draggedSubject = null;
                    this.clearDropTargets();
                });
            }

            // ドロップターゲット
            cell.addEventListener('dragover', (e) => {
                e.preventDefault();
                if (this.draggedSubject && !cell.classList.contains('has-subject')) {
                    cell.classList.add('drop-target');
                }
            });

            cell.addEventListener('dragleave', (e) => {
                cell.classList.remove('drop-target');
            });

            cell.addEventListener('drop', (e) => {
                e.preventDefault();
                cell.classList.remove('drop-target');
                
                if (this.draggedSubject) {
                    const newDay = cell.dataset.day;
                    const newPeriod = cell.dataset.period;
                    
                    if (newDay && newPeriod) {
                        this.moveSubject(this.draggedSubject.id, newDay, newPeriod);
                    }
                }
            });
        });
    }

    // ドロップターゲットをクリア
    clearDropTargets() {
        document.querySelectorAll('.drop-target').forEach(cell => {
            cell.classList.remove('drop-target');
        });
    }

    // 科目詳細モーダルを表示
    showSubjectModal(subject) {
        this.currentSubject = subject;
        
        const modal = document.getElementById('subjectModal');
        const modalTitle = document.getElementById('modalTitle');
        const modalBody = document.getElementById('modalBody');
        
        modalTitle.textContent = subject.name;
        
        const details = [
            ['曜日・時限', `${subject.day}曜日 ${subject.period}限`],
            ['教室', subject.room || '未設定'],
            ['単位数', subject.credits ? `${subject.credits}単位` : '未設定'],
            ['教員', subject.teacher || '未設定'],
            ['評価割合', subject.evaluation || '未設定'],
            ['授業形態', subject.style || '未設定'],
            ['楽さ', subject.ease ? `${subject.ease}/5` : '未設定'],
            ['授業内容', subject.description || '未設定'],
            ['メモ', subject.memo || '未設定']
        ];

        const detailsHTML = details.map(([label, value]) => `
            <div class="subject-detail-item">
                <span class="subject-detail-label">${label}</span>
                <span class="subject-detail-value ${!value || value === '未設定' ? 'empty' : ''}">
                    ${this.escapeHtml(value)}
                </span>
            </div>
        `).join('');

        modalBody.innerHTML = `
            <div class="subject-detail-grid">
                ${detailsHTML}
            </div>
        `;
        
        // モーダルを開く前にbodyにクラスを追加
        document.body.classList.add('modal-open');
        modal.style.display = 'block';
    }

    // ツールチップ用のテキストを作成
    createTooltipText(subject) {
        const parts = [subject.name];
        
        if (subject.room) parts.push(`教室: ${subject.room}`);
        if (subject.teacher) parts.push(`教員: ${subject.teacher}`);
        if (subject.credits) parts.push(`単位数: ${subject.credits}`);
        if (subject.style) parts.push(`形態: ${subject.style}`);
        if (subject.ease) parts.push(`楽さ: ${subject.ease}/5`);
        
        return parts.join('\n');
    }

    // メッセージを表示
    showMessage(message, type = 'success') {
        // 既存のメッセージを削除
        const existingMessage = document.querySelector('.message');
        if (existingMessage) {
            existingMessage.remove();
        }

        // 新しいメッセージを作成
        const messageElement = document.createElement('div');
        messageElement.className = `message ${type}`;
        messageElement.textContent = message;

        // メッセージを挿入
        const container = document.querySelector('.container');
        const header = document.querySelector('header');
        container.insertBefore(messageElement, header.nextSibling);

        // 3秒後に自動削除
        setTimeout(() => {
            if (messageElement.parentNode) {
                messageElement.remove();
            }
        }, 3000);
    }

    // HTMLエスケープ
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// アプリケーションの初期化
let app;
document.addEventListener('DOMContentLoaded', () => {
    app = new TimetableApp();
}); 