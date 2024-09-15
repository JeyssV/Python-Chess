import pygame
import sys

pygame.init()
pygame.mixer.init()

info = pygame.display.Info()
SCREEN_WIDTH, SCREEN_HEIGHT = info.current_w, info.current_h

WIDTH, HEIGHT = min(720, SCREEN_WIDTH), min(720, SCREEN_HEIGHT)

window = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Catur")

move_sound = pygame.mixer.Sound('Sound/Move.wav')
capture_sound = pygame.mixer.Sound('Sound/Capture.wav')
gover_sound = pygame.mixer.Sound('Sound/Game_Over.wav')

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
SQUARE_COLOR1 = (240, 218, 181)
SQUARE_COLOR2 = (180, 137, 100)
HIGHLIGHT_COLOR = (0, 203, 6)
MOVE_HIGHLIGHT_COLOR = (0, 203, 6) 
MOVE_EAT_HIGHLIGHTCOLOR = (187, 0, 0)

SQUARE_SIZE = WIDTH // 8
PIECE_SIZE = SQUARE_SIZE - 20

PIECE_IMAGES = {
    'white_pawn': pygame.transform.scale(pygame.image.load('Icon/white_pawn.png'), (PIECE_SIZE, PIECE_SIZE)),
    'white_rook': pygame.transform.scale(pygame.image.load('Icon/white_rook.png'), (PIECE_SIZE, PIECE_SIZE)),
    'white_knight': pygame.transform.scale(pygame.image.load('Icon/white_knight.png'), (PIECE_SIZE, PIECE_SIZE)),
    'white_bishop': pygame.transform.scale(pygame.image.load('Icon/white_bishop.png'), (PIECE_SIZE, PIECE_SIZE)),
    'white_queen': pygame.transform.scale(pygame.image.load('Icon/white_queen.png'), (PIECE_SIZE, PIECE_SIZE)),
    'white_king': pygame.transform.scale(pygame.image.load('Icon/white_king.png'), (PIECE_SIZE, PIECE_SIZE)),
    'black_pawn': pygame.transform.scale(pygame.image.load('Icon/black_pawn.png'), (PIECE_SIZE, PIECE_SIZE)),
    'black_rook': pygame.transform.scale(pygame.image.load('Icon/black_rook.png'), (PIECE_SIZE, PIECE_SIZE)),
    'black_knight': pygame.transform.scale(pygame.image.load('Icon/black_knight.png'), (PIECE_SIZE, PIECE_SIZE)),
    'black_bishop': pygame.transform.scale(pygame.image.load('Icon/black_bishop.png'), (PIECE_SIZE, PIECE_SIZE)),
    'black_queen': pygame.transform.scale(pygame.image.load('Icon/black_queen.png'), (PIECE_SIZE, PIECE_SIZE)),
    'black_king': pygame.transform.scale(pygame.image.load('Icon/black_king.png'), (PIECE_SIZE, PIECE_SIZE)),
}

INITIAL_POSITIONS = {
    'white': {
        'pawn': [(6, i) for i in range(8)],
        'rook': [(7, 0), (7, 7)],
        'knight': [(7, 1), (7, 6)],
        'bishop': [(7, 2), (7, 5)],
        'queen': [(7, 3)],
        'king': [(7, 4)]
    },
    'black': {
        'pawn': [(1, i) for i in range(8)],
        'rook': [(0, 0), (0, 7)],
        'knight': [(0, 1), (0, 6)],
        'bishop': [(0, 2), (0, 5)],
        'queen': [(0, 3)],
        'king': [(0, 4)]
    }
}

def valid_moves_for_enemy_king(pieces, enemy_turn):
    enemy_king_position = pieces[enemy_turn]['king'][0]
    enemy_moves = []

    for color, piece_type in pieces.items():
        if color != enemy_turn:
            for piece, positions in piece_type.items():
                for row, col in positions:
                    moves = valid_moves(piece, row, col, pieces, color)
                    for move in moves:
                        if move == enemy_king_position:
                            enemy_moves.append(move)

    return enemy_moves

def ai_move_smart(pieces, turn, depth=2):
    def evaluate_position(pieces, turn):
        piece_values = {
            'pawn': 1, 'knight': 3, 'bishop': 3.25, 'rook': 5, 'queen': 9, 'king': 1000
        }

        total_score = 0
        enemy_turn = 'white' if turn == 'black' else 'black'
        enemy_king_position = pieces[enemy_turn]['king'][0]

        ai_king_position = pieces[turn]['king'][0]

        for color, piece_type in pieces.items():
            for piece, positions in piece_type.items():
                for row, col in positions:
                    value = piece_values[piece]

                    if piece == 'pawn':
                        if col > 0 and (row + 1, col - 1) not in positions and (row - 1, col - 1) not in positions:
                            value -= 0.2

                    if piece in ['pawn', 'knight', 'bishop']:
                        if 2 <= row <= 5 and 2 <= col <= 5:
                            value += 0.5 

                    if piece == 'king':
                        if 1 <= row <= 6 and 1 <= col <= 6:
                            value -= 0.5 

                    if enemy_king_position:
                        enemy_king_row, enemy_king_col = enemy_king_position
                        distance_to_king = abs(row - enemy_king_row) + abs(col - enemy_king_col)

                        if piece in ['knight', 'bishop', 'queen', 'rook']:
                            value += (10 - distance_to_king) * 0.3 
                            if distance_to_king == 1:
                                value += 5 

                    moves = valid_moves(piece, row, col, pieces, color)
                    value += len(moves) * 0.1 

                    if color == turn:
                        total_score += value
                    else:
                        total_score -= value

                    if piece == 'king' and color == turn:
                        enemy_moves = valid_moves_for_enemy_king(pieces, enemy_turn)
                        if ai_king_position in enemy_moves:
                            total_score -= 10 

        return total_score

    def minimax(pieces, depth, alpha, beta, maximizing_player, turn):
        winner = check_winner(pieces)
        if winner:
            return (1000 if winner == 'black' else -1000) if maximizing_player else (-1000 if winner == 'black' else 1000)

        if depth == 0:
            return evaluate_position(pieces, turn)

        if maximizing_player:
            max_eval = -float('inf')
            for piece, positions in pieces['black'].items():
                for start_row, start_col in positions:
                    moves = valid_moves(piece, start_row, start_col, pieces, 'black')
                    for move in moves:
                        end_row, end_col = move
                        
                        enemy_king_position = pieces['white']['king'][0]
                        if (end_row, end_col) == enemy_king_position:
                            return 1000

                        pieces_copy = {k: {p: pos.copy() for p, pos in v.items()} for k, v in pieces.items()}
                        target = piece_at(pieces_copy, end_row, end_col)
                        if target:
                            pieces_copy[target[0]][target[1]].remove((end_row, end_col))
                        pieces_copy['black'][piece].remove((start_row, start_col))
                        pieces_copy['black'][piece].append((end_row, end_col))

                        eval = minimax(pieces_copy, depth - 1, alpha, beta, False, 'white')
                        max_eval = max(max_eval, eval)
                        alpha = max(alpha, eval)
                        if beta <= alpha:
                            break
            return max_eval
        else:
            min_eval = float('inf')
            for piece, positions in pieces['white'].items():
                for start_row, start_col in positions:
                    moves = valid_moves(piece, start_row, start_col, pieces, 'white')
                    for move in moves:
                        end_row, end_col = move

                        enemy_king_position = pieces['black']['king'][0]
                        if (end_row, end_col) == enemy_king_position:
                            return -1000

                        pieces_copy = {k: {p: pos.copy() for p, pos in v.items()} for k, v in pieces.items()}
                        target = piece_at(pieces_copy, end_row, end_col)
                        if target:
                            pieces_copy[target[0]][target[1]].remove((end_row, end_col))
                        pieces_copy['white'][piece].remove((start_row, start_col))
                        pieces_copy['white'][piece].append((end_row, end_col))

                        eval = minimax(pieces_copy, depth - 1, alpha, beta, True, 'black')
                        min_eval = min(min_eval, eval)
                        beta = min(beta, eval)
                        if beta <= alpha:
                            break
            return min_eval

    best_move = None
    best_score = -float('inf')

    for piece, positions in pieces['black'].items():
        for start_row, start_col in positions:
            moves = valid_moves(piece, start_row, start_col, pieces, 'black')
            for move in moves:
                end_row, end_col = move

                pieces_copy = {k: {p: pos.copy() for p, pos in v.items()} for k, v in pieces.items()}
                target = piece_at(pieces_copy, end_row, end_col)
                enemy_king_position = pieces['white']['king'][0]
                if (end_row, end_col) == enemy_king_position:
                    pieces[target[0]][target[1]].remove((end_row, end_col))
                    pieces['black'][piece].remove((start_row, start_col))
                    pieces['black'][piece].append((end_row, end_col))
                    return

                if target:
                    pieces_copy[target[0]][target[1]].remove((end_row, end_col))
                pieces_copy['black'][piece].remove((start_row, start_col))
                pieces_copy['black'][piece].append((end_row, end_col))

                score = minimax(pieces_copy, depth - 1, -float('inf'), float('inf'), False, 'black')
                if score > best_score:
                    best_move = (piece, (start_row, start_col), (end_row, end_col))
                    best_score = score

    if best_move:
        piece, (start_row, start_col), (end_row, end_col) = best_move
        target = piece_at(pieces, end_row, end_col)
        move_sound.play()

        if target and target[0] != turn:
            target_color, target_piece = target
            pieces[target_color][target_piece].remove((end_row, end_col))
            winner = check_winner(pieces)

            if not winner:
                capture_sound.play()

        pieces[turn][piece].remove((start_row, start_col))
        pieces[turn][piece].append((end_row, end_col))

def draw_board():
    for row in range(8):
        for col in range(8):
            color = SQUARE_COLOR1 if (row + col) % 2 == 0 else SQUARE_COLOR2
            pygame.draw.rect(window, color, pygame.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

def draw_pieces(pieces):
    for color, piece_type in pieces.items():
        for piece, positions in piece_type.items():
            for row, col in positions:
                piece_name = f'{color}_{piece}'
                window.blit(PIECE_IMAGES[piece_name], (col * SQUARE_SIZE + 10, row * SQUARE_SIZE + 10))

def piece_at(pieces, row, col):
    for color, piece_type in pieces.items():
        for piece, positions in piece_type.items():
            if (row, col) in positions:
                return color, piece
    return None

def valid_moves(piece_type, start_row, start_col, pieces, turn):
    moves = []
    direction = 1 if turn == 'black' else -1

    def add_move(r, c):
        if 0 <= r < 8 and 0 <= c < 8:
            target = piece_at(pieces, r, c)
            if target is None or target[0] != turn:
                moves.append((r, c))

    if piece_type == 'pawn':
        forward_row = start_row + direction
        if piece_at(pieces, forward_row, start_col) is None:
            moves.append((forward_row, start_col)) 
            if (turn == 'white' and start_row == 6) or (turn == 'black' and start_row == 1):
                forward_two_rows = forward_row + direction
                if piece_at(pieces, forward_two_rows, start_col) is None:
                    moves.append((forward_two_rows, start_col))
        for dc in [-1, 1]:
            new_col = start_col + dc
            if 0 <= new_col < 8:
                target = piece_at(pieces, forward_row, new_col)
                if target and target[0] != turn:
                    moves.append((forward_row, new_col))

    elif piece_type == 'knight':
        knight_moves = [
            (start_row + 2, start_col + 1), (start_row + 2, start_col - 1),
            (start_row - 2, start_col + 1), (start_row - 2, start_col - 1),
            (start_row + 1, start_col + 2), (start_row + 1, start_col - 2),
            (start_row - 1, start_col + 2), (start_row - 1, start_col - 2)
        ]
        for r, c in knight_moves:
            add_move(r, c)

    elif piece_type in ['rook', 'bishop', 'queen']:
        directions = []
        if piece_type in ['rook', 'queen']:
            directions += [(1, 0), (-1, 0), (0, 1), (0, -1)]  
        if piece_type in ['bishop', 'queen']:
            directions += [(1, 1), (-1, -1), (1, -1), (-1, 1)]  

        for dr, dc in directions:
            r, c = start_row, start_col
            while True:
                r += dr
                c += dc
                if 0 <= r < 8 and 0 <= c < 8:
                    target = piece_at(pieces, r, c)
                    if target is None:
                        moves.append((r, c))
                    elif target[0] != turn:
                        moves.append((r, c))
                        break
                    else:
                        break 
                else:
                    break

    elif piece_type == 'king':
        king_moves = [
            (start_row + 1, start_col), (start_row - 1, start_col),
            (start_row, start_col + 1), (start_row, start_col - 1),
            (start_row + 1, start_col + 1), (start_row - 1, start_col - 1),
            (start_row + 1, start_col - 1), (start_row - 1, start_col + 1)
        ]
        for r, c in king_moves:
            add_move(r, c)

    return moves

def highlight_square(row, col, color, border_width=4):
    pygame.draw.rect(window, color, pygame.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), border_width)

def promote_pawn(color, row, col):
    options = ['Ratu', 'Benteng', 'Gajah', 'Kuda']  
    promotion_map = {
        'Ratu': 'queen',
        'Benteng': 'rook',
        'Gajah': 'bishop',
        'Kuda': 'knight'
    }

    font = pygame.font.Font(None, 36)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                index = y // 100
                if 0 <= index < 4:
                    return promotion_map[options[index]]

        window.fill(WHITE)
        for i, option in enumerate(options):
            text = font.render(option.capitalize(), True, BLACK)
            window.blit(text, (WIDTH // 2 - text.get_width() // 2, i * 100 + 50))

        pygame.display.flip()

def check_winner(pieces):
    white_king = pieces['white']['king']
    black_king = pieces['black']['king']
    
    if not white_king:
        return 'black'
    elif not black_king:
        return 'white'
    return None

def display_winner(winner):
    font = pygame.font.Font(None, 72)
    message = f"{'Putih' if winner == 'white' else 'Hitam'} Menang!"
    text = font.render(message, True, BLACK)
    gover_sound.play()

    blur_surface = pygame.Surface((WIDTH, HEIGHT))
    blur_surface.set_alpha(128)
    blur_surface.fill(WHITE)
    
    window.blit(blur_surface, (0, 0))
    window.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2))
    pygame.display.flip()

    pygame.time.wait(3000)

def reset_game(mode):
    pieces = {'white': {}, 'black': {}}
    for color, piece_type in INITIAL_POSITIONS.items():
        for piece, positions in piece_type.items():
            pieces[color][piece] = positions.copy() 
    return pieces, 'white', None, [], mode

def main_menu():
    font = pygame.font.Font(None, 72)
    play_pvp_text = font.render('Pemain vs Pemain', True, BLACK)
    play_ai_text = font.render('Pemain vs AI', True, BLACK)
    
    while True:
        window.fill(WHITE)
        window.blit(play_pvp_text, (WIDTH // 2 - play_pvp_text.get_width() // 2, HEIGHT // 3))
        window.blit(play_ai_text, (WIDTH // 2 - play_ai_text.get_width() // 2, HEIGHT // 2))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                if HEIGHT // 3 <= y <= HEIGHT // 3 + 72:
                    return 'pvp'
                elif HEIGHT // 2 <= y <= HEIGHT // 2 + 72:
                    return 'ai'

        pygame.display.flip()

def main():
    clock = pygame.time.Clock()
    game_mode = main_menu()

    pieces, turn, selected_piece, valid_moves_list, mode = reset_game(game_mode)
    ai_thinking_start = None 
    ai_delay = 1500 

    while True:
        draw_board()
        draw_pieces(pieces)

        if selected_piece:
            start_row, start_col = selected_piece
            highlight_square(start_row, start_col, HIGHLIGHT_COLOR, border_width=4)
            for move_row, move_col in valid_moves_list:
                target = piece_at(pieces, move_row, move_col)
                if target and target[0] != turn:
                    highlight_square(move_row, move_col, MOVE_EAT_HIGHLIGHTCOLOR, border_width=4)
                else:
                    highlight_square(move_row, move_col, MOVE_HIGHLIGHT_COLOR, border_width=4)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if mode == 'pvp':
                if event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = pygame.mouse.get_pos()
                    row, col = y // SQUARE_SIZE, x // SQUARE_SIZE
                    clicked_piece = piece_at(pieces, row, col)

                    if selected_piece:
                        if (row, col) in valid_moves_list:
                            color, piece = piece_at(pieces, selected_piece[0], selected_piece[1])
                            pieces[color][piece].remove(selected_piece)
                            move_sound.play()

                            target = piece_at(pieces, row, col)
                            if target and target[0] != turn:
                                target_color, target_piece = target
                                pieces[target_color][target_piece].remove((row, col))

                                winner = check_winner(pieces)
                                if not winner:
                                    capture_sound.play()

                            pieces[color][piece].append((row, col))

                            if piece == 'pawn' and (row == 0 or row == 7):
                                if not winner:
                                    promoted_piece = promote_pawn(turn, row, col)
                                    pieces[color][piece].remove((row, col))

                                    if promoted_piece:
                                        pieces[color][promoted_piece].append((row, col))

                            winner = check_winner(pieces)
                            if winner:
                                display_winner(winner)
                                pieces, turn, selected_piece, valid_moves_list, mode = reset_game(game_mode)
                            else:
                                turn = 'black' if turn == 'white' else 'white'

                        selected_piece = None
                        valid_moves_list = []

                    elif clicked_piece and clicked_piece[0] == turn:
                        selected_piece = (row, col)
                        valid_moves_list = valid_moves(clicked_piece[1], row, col, pieces, turn)

            if turn == 'white' and mode == 'ai':
                if event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = pygame.mouse.get_pos()
                    row, col = y // SQUARE_SIZE, x // SQUARE_SIZE
                    clicked_piece = piece_at(pieces, row, col)

                    if selected_piece:
                        if (row, col) in valid_moves_list:
                            color, piece = piece_at(pieces, selected_piece[0], selected_piece[1])
                            pieces[color][piece].remove(selected_piece)
                            move_sound.play()

                            target = piece_at(pieces, row, col)
                            if target and target[0] != turn:
                                target_color, target_piece = target
                                pieces[target_color][target_piece].remove((row, col))

                                winner = check_winner(pieces)
                                if not winner:
                                    capture_sound.play()

                            pieces[color][piece].append((row, col))

                            if piece == 'pawn' and (row == 0 or row == 7):
                                if not winner:
                                    promoted_piece = promote_pawn(turn, row, col)
                                    pieces[color][piece].remove((row, col))

                                    if promoted_piece:
                                        pieces[color][promoted_piece].append((row, col))

                            winner = check_winner(pieces)
                            if winner:
                                display_winner(winner)
                                pieces, turn, selected_piece, valid_moves_list, mode = reset_game(game_mode)
                            else:
                                turn = 'black'

                        selected_piece = None
                        valid_moves_list = []

                    elif clicked_piece and clicked_piece[0] == turn:
                        selected_piece = (row, col)
                        valid_moves_list = valid_moves(clicked_piece[1], row, col, pieces, turn)

        if turn == 'black' and mode == 'ai':
            if not ai_thinking_start:
                ai_thinking_start = pygame.time.get_ticks()

            if pygame.time.get_ticks() - ai_thinking_start > ai_delay:
                ai_move_smart(pieces, turn)
                winner = check_winner(pieces)

                if winner:
                    display_winner(winner)
                    pieces, turn, selected_piece, valid_moves_list, mode = reset_game(game_mode)
                else:
                    turn = 'white'
                ai_thinking_start = None

        pygame.display.flip()
        clock.tick(30)

if __name__ == '__main__':
    main()
